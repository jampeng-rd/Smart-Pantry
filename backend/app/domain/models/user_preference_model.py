"""使用者偏好設定資料表模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.domain.models.base import Base


class UserPreference(Base):
    """儲存使用者主題、時區與提醒偏好。"""

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=False)
    theme: Mapped[str] = mapped_column(String(32), nullable=False, default="dark-soft")
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="zh-TW")
    expiration_email_reminder_days: Mapped[str] = mapped_column(String(8), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="user_preference")
