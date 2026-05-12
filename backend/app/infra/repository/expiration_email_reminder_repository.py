"""到期 Email 提醒資料存取層。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from backend.app.domain.models.expiration_reminder_delivery_model import ExpirationReminderDelivery
from backend.app.domain.models.pantry_item_model import PantryItem
from backend.app.domain.models.user_model import User
from backend.app.domain.models.user_preference_model import UserPreference


class ExpirationEmailReminderRepository:
    """封裝到期提醒查詢、寄送紀錄建立與狀態更新。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def list_users_with_preferences(self) -> list[tuple[User, UserPreference | None]]:
        """列出所有使用者與其偏好設定（可為空）。"""
        statement = (
            select(User, UserPreference)
            .outerjoin(UserPreference, UserPreference.user_id == User.id)
            .order_by(asc(User.id))
        )
        return list(self.db.execute(statement).all())

    def list_items_by_user_and_expiration_date(self, user_id: int, expiration_date: date) -> list[PantryItem]:
        """查詢使用者在指定到期日的食材。"""
        statement = (
            select(PantryItem)
            .where(PantryItem.user_id == user_id, PantryItem.expiration_date == expiration_date)
            .order_by(asc(PantryItem.expiration_date), asc(PantryItem.id))
        )
        return list(self.db.execute(statement).scalars().all())

    def has_success_delivery(self, user_id: int, scheduled_date: date, send_window: str) -> bool:
        """檢查同日同時段是否已有成功寄送。"""
        statement = select(ExpirationReminderDelivery.id).where(
            ExpirationReminderDelivery.user_id == user_id,
            ExpirationReminderDelivery.scheduled_date == scheduled_date,
            ExpirationReminderDelivery.send_window == send_window,
            ExpirationReminderDelivery.status == "success",
        )
        return self.db.execute(statement).first() is not None

    def create_delivery(
        self,
        user_id: int,
        scheduled_date: date,
        send_window: str,
        reminder_days: str,
        item_ids: list[int],
        email_to: str,
    ) -> ExpirationReminderDelivery:
        """建立寄送紀錄（pending）。"""
        row = ExpirationReminderDelivery(
            user_id=user_id,
            scheduled_date=scheduled_date,
            send_window=send_window,
            reminder_days=reminder_days,
            item_ids=item_ids,
            email_to=email_to,
            status="pending",
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def mark_delivery_success(self, row: ExpirationReminderDelivery, sent_at: datetime) -> ExpirationReminderDelivery:
        """將寄送紀錄更新為成功。"""
        row.status = "success"
        row.sent_at = sent_at
        row.error_message = None
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def mark_delivery_failed(self, row: ExpirationReminderDelivery, error_message: str) -> ExpirationReminderDelivery:
        """將寄送紀錄更新為失敗。"""
        row.status = "failed"
        row.error_message = error_message
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
