"""Billing 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json

import pytest
from fastapi import HTTPException

from backend.app.infra.newebpay import NewebPayCrypto
from backend.app.infra.settings import Settings
from backend.app.services.billing_service import BillingService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int
    email: str = "user@example.com"


@dataclass
class FakeMembership:
    """測試用會員資料。"""

    id: int
    user_id: int
    provider: str
    billing_mode: str
    tier: str
    membership_status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None


@dataclass
class FakeTransaction:
    """測試用交易資料。"""

    id: int
    user_id: int
    external_trade_no: str
    amount: float
    transaction_status: str = "pending"
    provider_reference: str | None = None
    paid_at: datetime | None = None
    failed_at: datetime | None = None
    membership_id: int | None = None


@dataclass
class FakeEvent:
    """測試用 webhook 事件資料。"""

    id: int
    processing_status: str = "received"
    error_message: str | None = None


class FakeDbSession:
    """最小 DB 介面 stub。"""

    def add(self, _value) -> None:
        pass

    def commit(self) -> None:
        pass


class FakeBillingRepository:
    """以記憶體模擬 BillingRepository。"""

    def __init__(self) -> None:
        self.db = FakeDbSession()
        self.users: dict[int, FakeUser] = {1: FakeUser(id=1)}
        self.membership: FakeMembership | None = None
        self.membership_id_seq = 9
        self.transactions: dict[str, FakeTransaction] = {}
        self.events: list[dict] = []
        self.mark_success_count = 0

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        return self.users.get(user_id)

    def get_latest_membership(self, user_id: int) -> FakeMembership | None:
        if self.membership and self.membership.user_id == user_id:
            return self.membership
        return None

    def create_transaction(self, user_id: int, amount: float, external_trade_no: str, description: str) -> FakeTransaction:
        transaction = FakeTransaction(
            id=len(self.transactions) + 1,
            user_id=user_id,
            external_trade_no=external_trade_no,
            amount=amount,
        )
        self.transactions[external_trade_no] = transaction
        return transaction

    def get_transaction_by_trade_no(self, external_trade_no: str) -> FakeTransaction | None:
        return self.transactions.get(external_trade_no)

    def get_transaction_for_user(self, user_id: int, external_trade_no: str) -> FakeTransaction | None:
        transaction = self.transactions.get(external_trade_no)
        if transaction and transaction.user_id == user_id:
            return transaction
        return None

    def create_webhook_event(self, **kwargs) -> FakeEvent:
        self.events.append(kwargs)
        return FakeEvent(id=len(self.events))

    def mark_webhook_event_processed(self, event: FakeEvent, processing_status: str, error_message: str | None = None) -> FakeEvent:
        event.processing_status = processing_status
        event.error_message = error_message
        return event

    def mark_transaction_success(self, transaction: FakeTransaction, *, provider_reference: str | None, paid_at: datetime) -> FakeTransaction:
        self.mark_success_count += 1
        transaction.transaction_status = "success"
        transaction.provider_reference = provider_reference
        transaction.paid_at = paid_at
        return transaction

    def mark_transaction_failed(self, transaction: FakeTransaction, *, provider_reference: str | None, failed_at: datetime) -> FakeTransaction:
        transaction.transaction_status = "failed"
        transaction.provider_reference = provider_reference
        transaction.failed_at = failed_at
        return transaction

    def activate_or_create_pro_membership(self, user_id: int) -> FakeMembership:
        if self.membership is None:
            self.membership_id_seq += 1
            self.membership = FakeMembership(
                id=self.membership_id_seq,
                user_id=user_id,
                provider="newebpay",
                billing_mode="one_time",
                tier="PRO",
                membership_status="active",
                started_at=datetime.now(timezone.utc),
                ended_at=None,
            )
        else:
            self.membership.provider = "newebpay"
            self.membership.billing_mode = "one_time"
            self.membership.tier = "PRO"
            self.membership.membership_status = "active"
            self.membership.ended_at = None
        return self.membership


@pytest.fixture
def billing_service_one_time() -> tuple[BillingService, FakeBillingRepository]:
    repository = FakeBillingRepository()
    settings = Settings(
        billing_mode="one_time",
        newebpay_merchant_id="MS123456789",
        newebpay_hash_key="12345678901234567890123456789012",
        newebpay_hash_iv="1234567890123456",
        newebpay_notify_url="https://example.com/notify",
        newebpay_return_url="https://example.com/newebpay/return",
        newebpay_frontend_result_url="https://example.com/result",
        newebpay_customer_back_url="https://example.com/upgrade",
    )
    return BillingService(repository=repository, settings=settings), repository


def _build_notify_payload(service: BillingService, merchant_order_no: str, status_text: str, trade_no: str = "NEWEBPAY-001") -> dict[str, str]:
    crypto = NewebPayCrypto(
        hash_key=service.settings.newebpay_hash_key,
        hash_iv=service.settings.newebpay_hash_iv,
    )
    decrypted = {
        "Status": status_text,
        "Message": "模擬通知",
        "Result": {
            "MerchantOrderNo": merchant_order_no,
            "TradeNo": trade_no,
            "Amt": 99,
        },
    }
    json_text = json.dumps(decrypted, ensure_ascii=False)
    pad_size = 16 - (len(json_text.encode("utf-8")) % 16)
    plain = json_text.encode("utf-8") + bytes([pad_size] * pad_size)
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    cipher = Cipher(
        algorithms.AES(service.settings.newebpay_hash_key.encode("utf-8")),
        modes.CBC(service.settings.newebpay_hash_iv.encode("utf-8")),
    )
    encryptor = cipher.encryptor()
    trade_info = (encryptor.update(plain) + encryptor.finalize()).hex()
    return {"TradeInfo": trade_info, "TradeSha": crypto.generate_trade_sha(trade_info)}


def test_upgrade_entry_should_return_one_time_path(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, _ = billing_service_one_time
    data = service.get_upgrade_entry(user_id=1)
    assert data.billing_mode == "one_time"
    assert data.upgrade_entry_path == "/billing/newebpay-one-time"


def test_checkout_should_create_transaction_and_payload(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, repository = billing_service_one_time
    data = service.create_newebpay_one_time_checkout(user_id=1)
    assert data.external_trade_no in repository.transactions
    assert data.gateway_url == "https://ccore.newebpay.com/MPG/mpg_gateway"
    assert data.merchant_id == "MS123456789"


def test_checkout_should_reject_when_user_is_already_pro_active(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, repository = billing_service_one_time
    repository.membership = FakeMembership(
        id=99,
        user_id=1,
        provider="newebpay",
        billing_mode="one_time",
        tier="PRO",
        membership_status="active",
        started_at=datetime.now(timezone.utc),
        ended_at=None,
    )

    with pytest.raises(HTTPException) as exc:
        service.create_newebpay_one_time_checkout(user_id=1)

    assert exc.value.status_code == 409
    assert "已是 PRO" in str(exc.value.detail)


def test_notify_success_should_upgrade_once(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, repository = billing_service_one_time
    checkout = service.create_newebpay_one_time_checkout(user_id=1)
    payload = _build_notify_payload(service=service, merchant_order_no=checkout.external_trade_no, status_text="SUCCESS")

    service.handle_newebpay_notify(payload=payload)
    service.handle_newebpay_notify(payload=payload)

    transaction = repository.transactions[checkout.external_trade_no]
    assert transaction.transaction_status == "success"
    assert repository.membership is not None
    assert repository.membership.tier == "PRO"
    assert repository.mark_success_count == 1


def test_notify_failed_should_not_upgrade(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, repository = billing_service_one_time
    checkout = service.create_newebpay_one_time_checkout(user_id=1)
    payload = _build_notify_payload(service=service, merchant_order_no=checkout.external_trade_no, status_text="FAILED")

    service.handle_newebpay_notify(payload=payload)

    transaction = repository.transactions[checkout.external_trade_no]
    assert transaction.transaction_status == "failed"
    assert repository.membership is None


def test_notify_invalid_sha_should_reject(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    service, repository = billing_service_one_time
    checkout = service.create_newebpay_one_time_checkout(user_id=1)
    payload = _build_notify_payload(service=service, merchant_order_no=checkout.external_trade_no, status_text="SUCCESS")
    payload["TradeSha"] = "INVALID_SHA"

    with pytest.raises(HTTPException) as exc:
        service.handle_newebpay_notify(payload=payload)

    assert exc.value.status_code == 400
    assert repository.membership is None


def test_build_return_redirect_url_should_use_merchant_order_no_from_payload(
    billing_service_one_time: tuple[BillingService, FakeBillingRepository],
) -> None:
    service, _ = billing_service_one_time
    redirect_url = service.build_newebpay_return_redirect_url(payload={"MerchantOrderNo": "SP123"})
    assert redirect_url == "https://example.com/result?external_trade_no=SP123"


def test_build_return_redirect_url_should_extract_from_trade_info(
    billing_service_one_time: tuple[BillingService, FakeBillingRepository],
) -> None:
    service, _ = billing_service_one_time
    payload = _build_notify_payload(service=service, merchant_order_no="SPFROMTRADEINFO", status_text="SUCCESS")
    redirect_url = service.build_newebpay_return_redirect_url(payload=payload)
    assert redirect_url == "https://example.com/result?external_trade_no=SPFROMTRADEINFO"
