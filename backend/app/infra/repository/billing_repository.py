"""Billing 資料存取層。"""

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

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
