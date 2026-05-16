"""Billing 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from backend.app.infra.settings import Settings
from backend.app.services.billing_service import BillingService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int


@dataclass
class FakeMembership:
    """測試用會員資料。"""

    user_id: int
    provider: str
    billing_mode: str
    tier: str
    membership_status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None


class FakeBillingRepository:
    """以記憶體模擬 BillingRepository。"""

    def __init__(self) -> None:
        self.users: dict[int, FakeUser] = {1: FakeUser(id=1)}
        self.memberships: dict[int, FakeMembership] = {}

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        """依 ID 取得使用者。"""
        return self.users.get(user_id)

    def get_latest_membership(self, user_id: int) -> FakeMembership | None:
        """取得最新會員資料。"""
        return self.memberships.get(user_id)


@pytest.fixture
def billing_service_one_time() -> tuple[BillingService, FakeBillingRepository]:
    """建立 one_time 模式服務。"""
    repository = FakeBillingRepository()
    settings = Settings(billing_mode="one_time")
    return BillingService(repository=repository, settings=settings), repository


@pytest.fixture
def billing_service_subscription() -> tuple[BillingService, FakeBillingRepository]:
    """建立 subscription 模式服務。"""
    repository = FakeBillingRepository()
    settings = Settings(billing_mode="subscription")
    return BillingService(repository=repository, settings=settings), repository


def test_upgrade_entry_should_return_one_time_path(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    """one_time 模式應回傳單次付款入口。"""
    service, _ = billing_service_one_time

    data = service.get_upgrade_entry(user_id=1)

    assert data.billing_mode == "one_time"
    assert data.upgrade_entry_path == "/billing/newebpay-one-time"
    assert data.membership.is_pro is False
    assert data.membership.tier == "FREE"


def test_upgrade_entry_should_return_subscription_path(
    billing_service_subscription: tuple[BillingService, FakeBillingRepository],
) -> None:
    """subscription 模式應回傳訂閱入口。"""
    service, _ = billing_service_subscription

    data = service.get_upgrade_entry(user_id=1)

    assert data.billing_mode == "subscription"
    assert data.upgrade_entry_path == "/billing/newebpay-subscription"


def test_upgrade_entry_should_reflect_pro_membership(
    billing_service_subscription: tuple[BillingService, FakeBillingRepository],
) -> None:
    """有有效 PRO 會員時應回傳 is_pro=True。"""
    service, repository = billing_service_subscription
    repository.memberships[1] = FakeMembership(
        user_id=1,
        provider="newebpay",
        billing_mode="subscription",
        tier="PRO",
        membership_status="active",
        started_at=datetime.now(timezone.utc),
    )

    data = service.get_upgrade_entry(user_id=1)

    assert data.membership.is_pro is True
    assert data.membership.provider == "newebpay"
    assert data.membership.membership_status == "active"


def test_upgrade_entry_should_reject_unknown_user(billing_service_one_time: tuple[BillingService, FakeBillingRepository]) -> None:
    """查無使用者時應回 404。"""
    service, _ = billing_service_one_time

    with pytest.raises(HTTPException) as exc:
        service.get_upgrade_entry(user_id=999)

    assert exc.value.status_code == 404
