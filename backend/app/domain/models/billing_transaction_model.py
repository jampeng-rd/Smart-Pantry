"""Billing 交易資料表模型。"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.domain.models.base import Base


class BillingTransaction(Base):
    """記錄付款或扣款交易狀態。"""

    __tablename__ = "billing_transactions"
    __table_args__ = (
        Index("ix_billing_transactions_user_id_status", "user_id", "transaction_status"),
        Index("ix_billing_transactions_external_trade_no", "external_trade_no", unique=True),
        Index("ix_billing_transactions_provider_ref", "provider_reference"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    membership_id: Mapped[int | None] = mapped_column(ForeignKey("billing_memberships.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    billing_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="TWD")
    external_trade_no: Mapped[str] = mapped_column(String(80), nullable=False)
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")
    membership = relationship("BillingMembership")
