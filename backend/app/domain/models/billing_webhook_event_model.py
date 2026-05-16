"""Billing Webhook 事件記錄資料表模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.domain.models.base import Base


class BillingWebhookEvent(Base):
    """保存金流 callback/webhook 原始內容與處理結果。"""

    __tablename__ = "billing_webhook_events"
    __table_args__ = (
        Index("ix_billing_webhook_events_user_id", "user_id"),
        Index("ix_billing_webhook_events_provider_event_id", "provider_event_id"),
        Index("ix_billing_webhook_events_provider_event_type", "provider", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    billing_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    provider_event_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    event_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="received")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
