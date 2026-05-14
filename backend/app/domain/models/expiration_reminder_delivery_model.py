"""到期 Email 提醒寄送紀錄資料表模型。"""

from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.domain.models.base import Base


class ExpirationReminderDelivery(Base):
    """記錄到期提醒寄送狀態，避免同時段重複寄送。"""

    __tablename__ = "expiration_reminder_deliveries"
    __table_args__ = (
        Index("ix_expiration_reminder_user_date_window", "user_id", "scheduled_date", "send_window"),
        Index("ix_expiration_reminder_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    send_window: Mapped[str] = mapped_column(String(32), nullable=False)
    reminder_days: Mapped[str] = mapped_column(String(8), nullable=False)
    item_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    email_to: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    final_status: Mapped[str] = mapped_column(String(32), nullable=False, default="failed")
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="expiration_reminder_deliveries")
