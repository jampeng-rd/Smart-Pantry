"""Billing 商業邏輯服務。"""

from __future__ import annotations

from datetime import datetime, timezone
import random
from urllib.parse import urlencode

from fastapi import HTTPException, status

from backend.app.domain.schemas.billing_schema import (
    BillingMembershipSummary,
    BillingOneTimeCheckoutResponseData,
    BillingTransactionStatusResponseData,
    BillingUpgradeEntryResponseData,
)
from backend.app.infra.newebpay import NewebPayCrypto, get_newebpay_gateway_url
from backend.app.infra.repository.billing_repository import BillingRepository
from backend.app.infra.settings import Settings


class BillingService:
    """處理升級入口、單次付款與 callback。"""

    def __init__(self, repository: BillingRepository, settings: Settings):
        """建立服務實例。"""
        self.repository = repository
        self.settings = settings

    def get_upgrade_entry(self, user_id: int) -> BillingUpgradeEntryResponseData:
        """取得升級入口設定與目前會員狀態。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        membership = self.repository.get_latest_membership(user_id=user_id)
        summary = self._to_membership_summary(membership)

        if self.settings.billing_mode == "one_time":
            entry_path = "/billing/newebpay-one-time"
            message = "目前為單次付款模式，將導向藍新單次付款入口。"
        else:
            entry_path = "/billing/newebpay-subscription"
            message = "目前為訂閱制模式，將導向藍新訂閱付款入口。"

        return BillingUpgradeEntryResponseData(
            billing_mode=self.settings.billing_mode,
            upgrade_entry_path=entry_path,
            one_time_entry_path="/billing/newebpay-one-time",
            subscription_entry_path="/billing/newebpay-subscription",
            membership=summary,
            message=message,
        )

    def create_newebpay_one_time_checkout(self, user_id: int) -> BillingOneTimeCheckoutResponseData:
        """建立藍新單次付款交易與表單資料。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")
        self._validate_newebpay_settings()

        external_trade_no = self._build_merchant_order_no(user_id=user_id)
        transaction = self.repository.create_transaction(
            user_id=user_id,
            amount=99.0,
            external_trade_no=external_trade_no,
            description="Smart Pantry PRO 單次升級",
        )

        trade_payload = {
            "MerchantID": self.settings.newebpay_merchant_id,
            "RespondType": "JSON",
            "TimeStamp": str(int(datetime.now(timezone.utc).timestamp())),
            "Version": self.settings.newebpay_mpg_version,
            "LangType": "zh-tw",
            "MerchantOrderNo": external_trade_no,
            "Amt": "99",
            "ItemDesc": "Smart Pantry PRO 升級",
            "Email": user.email,
            "NotifyURL": self.settings.newebpay_notify_url,
            "ReturnURL": self.settings.newebpay_return_url,
            "ClientBackURL": self.settings.newebpay_customer_back_url,
            "CREDIT": "1",
        }
        crypto = NewebPayCrypto(hash_key=self.settings.newebpay_hash_key, hash_iv=self.settings.newebpay_hash_iv)
        trade_info = crypto.encrypt_trade_info(payload=trade_payload)
        trade_sha = crypto.generate_trade_sha(trade_info=trade_info)

        return BillingOneTimeCheckoutResponseData(
            transaction_id=transaction.id,
            external_trade_no=external_trade_no,
            gateway_url=get_newebpay_gateway_url(self.settings.newebpay_env),
            merchant_id=self.settings.newebpay_merchant_id,
            trade_info=trade_info,
            trade_sha=trade_sha,
            version=self.settings.newebpay_mpg_version,
        )

    def handle_newebpay_notify(self, payload: dict) -> str:
        """處理藍新背景通知。"""
        trade_info = str(payload.get("TradeInfo") or "")
        trade_sha = str(payload.get("TradeSha") or "")
        if not trade_info or not trade_sha:
            self.repository.create_webhook_event(
                user_id=None,
                event_type="notify",
                provider_event_id=None,
                event_summary="缺少 TradeInfo 或 TradeSha",
                payload=payload,
                processing_status="failed",
                error_message="缺少必要欄位",
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少必要欄位")

        crypto = NewebPayCrypto(hash_key=self.settings.newebpay_hash_key, hash_iv=self.settings.newebpay_hash_iv)
        if not crypto.verify_trade_sha(trade_info=trade_info, trade_sha=trade_sha):
            self.repository.create_webhook_event(
                user_id=None,
                event_type="notify",
                provider_event_id=None,
                event_summary="TradeSha 驗證失敗",
                payload=payload,
                processing_status="failed",
                error_message="TradeSha 驗證失敗",
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TradeSha 驗證失敗")

        decrypted = crypto.decrypt_trade_info(trade_info=trade_info)
        result = decrypted.get("Result", {}) if isinstance(decrypted, dict) else {}
        merchant_order_no = str(result.get("MerchantOrderNo") or "")
        trade_no = str(result.get("TradeNo") or "")
        status_text = str(decrypted.get("Status") or "")
        message = str(decrypted.get("Message") or "")

        transaction = self.repository.get_transaction_by_trade_no(external_trade_no=merchant_order_no)
        event = self.repository.create_webhook_event(
            user_id=transaction.user_id if transaction else None,
            event_type="notify",
            provider_event_id=trade_no or merchant_order_no or None,
            event_summary=message or status_text or "newebpay notify",
            payload={"raw_payload": payload, "decrypted": decrypted},
        )
        if transaction is None:
            self.repository.mark_webhook_event_processed(event, processing_status="failed", error_message="交易不存在")
            return "OK"

        # Idempotency: 同一筆成功通知重送時，不重複升級。
        if transaction.transaction_status == "success":
            self.repository.mark_webhook_event_processed(event, processing_status="duplicated")
            return "OK"

        is_success = status_text.upper() == "SUCCESS"
        provider_reference = trade_no or None
        now = datetime.now(timezone.utc)
        if is_success:
            membership = self.repository.activate_or_create_pro_membership(user_id=transaction.user_id)
            updated = self.repository.mark_transaction_success(
                transaction=transaction,
                provider_reference=provider_reference,
                paid_at=now,
            )
            if updated.membership_id is None:
                updated.membership_id = membership.id
                self.repository.db.add(updated)
                self.repository.db.commit()
            self.repository.mark_webhook_event_processed(event, processing_status="processed")
            return "OK"

        self.repository.mark_transaction_failed(
            transaction=transaction,
            provider_reference=provider_reference,
            failed_at=now,
        )
        self.repository.mark_webhook_event_processed(event, processing_status="processed")
        return "OK"

    def get_transaction_status(self, user_id: int, external_trade_no: str) -> BillingTransactionStatusResponseData:
        """提供前端結果頁查詢交易狀態。"""
        transaction = self.repository.get_transaction_for_user(user_id=user_id, external_trade_no=external_trade_no)
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="查無交易資料")

        membership = self.repository.get_latest_membership(user_id=user_id)
        summary = self._to_membership_summary(membership=membership)
        return BillingTransactionStatusResponseData(
            external_trade_no=transaction.external_trade_no,
            transaction_status=transaction.transaction_status,
            membership_status=summary.membership_status,
            is_pro=summary.is_pro,
            amount=float(transaction.amount),
            paid_at=transaction.paid_at,
            failed_at=transaction.failed_at,
        )

    def build_newebpay_return_redirect_url(self, payload: dict) -> str:
        """根據藍新前台返回資料建立前端結果頁導向 URL。"""
        external_trade_no = self._extract_external_trade_no(payload=payload)
        query = urlencode({"external_trade_no": external_trade_no}) if external_trade_no else ""
        joiner = "&" if "?" in self.settings.newebpay_frontend_result_url else "?"
        return f"{self.settings.newebpay_frontend_result_url}{joiner}{query}" if query else self.settings.newebpay_frontend_result_url

    def _validate_newebpay_settings(self) -> None:
        """驗證藍新設定是否齊全。"""
        missing_keys: list[str] = []
        if not self.settings.newebpay_merchant_id.strip():
            missing_keys.append("NEWEBPAY_MERCHANT_ID")
        if not self.settings.newebpay_hash_key.strip():
            missing_keys.append("NEWEBPAY_HASH_KEY")
        if not self.settings.newebpay_hash_iv.strip():
            missing_keys.append("NEWEBPAY_HASH_IV")
        if missing_keys:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"金流設定缺少必要欄位：{', '.join(missing_keys)}",
            )

    def _build_merchant_order_no(self, user_id: int) -> str:
        """產生符合藍新限制的 MerchantOrderNo。"""
        now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        suffix = f"{random.randint(0, 9999):04d}"
        candidate = f"SP{user_id}{now}{suffix}"
        return candidate[:30]

    def _extract_external_trade_no(self, payload: dict) -> str:
        """從藍新返回 payload 中提取 MerchantOrderNo。"""
        merchant_order_no = str(payload.get("MerchantOrderNo") or "").strip()
        if merchant_order_no:
            return merchant_order_no

        trade_info = str(payload.get("TradeInfo") or "").strip()
        trade_sha = str(payload.get("TradeSha") or "").strip()
        if not trade_info or not trade_sha:
            return ""

        crypto = NewebPayCrypto(hash_key=self.settings.newebpay_hash_key, hash_iv=self.settings.newebpay_hash_iv)
        if not crypto.verify_trade_sha(trade_info=trade_info, trade_sha=trade_sha):
            return ""
        decrypted = crypto.decrypt_trade_info(trade_info=trade_info)
        result = decrypted.get("Result", {}) if isinstance(decrypted, dict) else {}
        return str(result.get("MerchantOrderNo") or "").strip()

    @staticmethod
    def _to_membership_summary(membership) -> BillingMembershipSummary:
        """將會員資料轉換為摘要。"""
        return BillingMembershipSummary(
            is_pro=bool(membership and membership.tier.upper() == "PRO" and membership.membership_status in {"active", "trialing"}),
            tier=membership.tier if membership else "FREE",
            membership_status=membership.membership_status if membership else "inactive",
            provider=membership.provider if membership else None,
            billing_mode=membership.billing_mode if membership else None,
            started_at=membership.started_at if membership else None,
            ended_at=membership.ended_at if membership else None,
        )
