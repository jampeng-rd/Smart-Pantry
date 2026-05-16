"""Billing 資料存取層。"""

from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.domain.models.billing_transaction_model import BillingTransaction
from backend.app.domain.models.billing_webhook_event_model import BillingWebhookEvent
from backend.app.domain.models.billing_membership_model import BillingMembership
from backend.app.domain.models.user_model import User


class BillingRepository:
    """封裝 Billing 相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        """依使用者 ID 查詢使用者。"""
        statement = select(User).where(User.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_latest_membership(self, user_id: int) -> BillingMembership | None:
        """取得使用者最新一筆會員資料。"""
        statement = (
            select(BillingMembership)
            .where(BillingMembership.user_id == user_id)
            .order_by(desc(BillingMembership.updated_at), desc(BillingMembership.id))
            .limit(1)
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_transaction(
        self,
        user_id: int,
        amount: float,
        external_trade_no: str,
        description: str,
    ) -> BillingTransaction:
        """建立待付款交易。"""
        transaction = BillingTransaction(
            user_id=user_id,
            provider="newebpay",
            billing_mode="one_time",
            transaction_status="pending",
            amount=amount,
            currency="TWD",
            external_trade_no=external_trade_no,
            description=description,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transaction_by_trade_no(self, external_trade_no: str) -> BillingTransaction | None:
        """依商店訂單編號查詢交易。"""
        statement = select(BillingTransaction).where(BillingTransaction.external_trade_no == external_trade_no)
        return self.db.execute(statement).scalar_one_or_none()

    def get_transaction_for_user(self, user_id: int, external_trade_no: str) -> BillingTransaction | None:
        """查詢指定使用者交易。"""
        statement = select(BillingTransaction).where(
            BillingTransaction.user_id == user_id,
            BillingTransaction.external_trade_no == external_trade_no,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_webhook_event(
        self,
        *,
        user_id: int | None,
        event_type: str,
        provider_event_id: str | None,
        event_summary: str | None,
        payload: dict,
        processing_status: str = "received",
        error_message: str | None = None,
    ) -> BillingWebhookEvent:
        """寫入 webhook/callback 原始事件。"""
        event = BillingWebhookEvent(
            user_id=user_id,
            provider="newebpay",
            billing_mode="one_time",
            event_type=event_type,
            provider_event_id=provider_event_id,
            event_summary=event_summary,
            payload=payload,
            processing_status=processing_status,
            error_message=error_message,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_webhook_event_processed(
        self,
        event: BillingWebhookEvent,
        processing_status: str,
        error_message: str | None = None,
    ) -> BillingWebhookEvent:
        """更新 webhook 事件處理狀態。"""
        event.processing_status = processing_status
        event.error_message = error_message
        event.processed_at = datetime.now(timezone.utc)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_transaction_success(
        self,
        transaction: BillingTransaction,
        *,
        provider_reference: str | None,
        paid_at: datetime,
    ) -> BillingTransaction:
        """將交易標記為成功。"""
        transaction.transaction_status = "success"
        transaction.provider_reference = provider_reference
        transaction.paid_at = paid_at
        transaction.failed_at = None
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def mark_transaction_failed(
        self,
        transaction: BillingTransaction,
        *,
        provider_reference: str | None,
        failed_at: datetime,
    ) -> BillingTransaction:
        """將交易標記為失敗。"""
        transaction.transaction_status = "failed"
        transaction.provider_reference = provider_reference
        transaction.failed_at = failed_at
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def activate_or_create_pro_membership(self, user_id: int) -> BillingMembership:
        """啟用或建立 PRO 會員紀錄（單次付款 MVP: 永久有效）。"""
        membership = self.get_latest_membership(user_id=user_id)
        now = datetime.now(timezone.utc)

        if membership is None:
            membership = BillingMembership(
                user_id=user_id,
                provider="newebpay",
                billing_mode="one_time",
                tier="PRO",
                membership_status="active",
                started_at=now,
                ended_at=None,
            )
        else:
            membership.provider = "newebpay"
            membership.billing_mode = "one_time"
            membership.tier = "PRO"
            membership.membership_status = "active"
            membership.started_at = membership.started_at or now
            membership.ended_at = None

        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership
