"""phase 14-3 billing core models and upgrade entry

Revision ID: 20260516_1900
Revises: 20260515_1401
Create Date: 2026-05-16 19:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260516_1900"
down_revision = "20260515_1401"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """建立 Billing 共用核心資料表。"""
    op.create_table(
        "billing_memberships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("billing_mode", sa.String(length=20), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False),
        sa.Column("membership_status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_customer_ref", sa.String(length=120), nullable=True),
        sa.Column("provider_subscription_ref", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_billing_memberships_user_id", "billing_memberships", ["user_id"], unique=False)
    op.create_index("ix_billing_memberships_user_id_status", "billing_memberships", ["user_id", "membership_status"], unique=False)
    op.create_index("ix_billing_memberships_provider_mode", "billing_memberships", ["provider", "billing_mode"], unique=False)

    op.create_table(
        "billing_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("membership_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("billing_mode", sa.String(length=20), nullable=False),
        sa.Column("transaction_status", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("external_trade_no", sa.String(length=80), nullable=False),
        sa.Column("provider_reference", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["membership_id"], ["billing_memberships.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_billing_transactions_user_id", "billing_transactions", ["user_id"], unique=False)
    op.create_index("ix_billing_transactions_user_id_status", "billing_transactions", ["user_id", "transaction_status"], unique=False)
    op.create_index("ix_billing_transactions_external_trade_no", "billing_transactions", ["external_trade_no"], unique=True)
    op.create_index("ix_billing_transactions_provider_ref", "billing_transactions", ["provider_reference"], unique=False)

    op.create_table(
        "billing_webhook_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("billing_mode", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("provider_event_id", sa.String(length=120), nullable=True),
        sa.Column("event_summary", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_billing_webhook_events_user_id", "billing_webhook_events", ["user_id"], unique=False)
    op.create_index("ix_billing_webhook_events_provider_event_id", "billing_webhook_events", ["provider_event_id"], unique=False)
    op.create_index(
        "ix_billing_webhook_events_provider_event_type",
        "billing_webhook_events",
        ["provider", "event_type"],
        unique=False,
    )


def downgrade() -> None:
    """回滾 Billing 共用核心資料表。"""
    op.drop_index("ix_billing_webhook_events_provider_event_type", table_name="billing_webhook_events")
    op.drop_index("ix_billing_webhook_events_provider_event_id", table_name="billing_webhook_events")
    op.drop_index("ix_billing_webhook_events_user_id", table_name="billing_webhook_events")
    op.drop_table("billing_webhook_events")

    op.drop_index("ix_billing_transactions_provider_ref", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_external_trade_no", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_user_id_status", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_user_id", table_name="billing_transactions")
    op.drop_table("billing_transactions")

    op.drop_index("ix_billing_memberships_provider_mode", table_name="billing_memberships")
    op.drop_index("ix_billing_memberships_user_id_status", table_name="billing_memberships")
    op.drop_index("ix_billing_memberships_user_id", table_name="billing_memberships")
    op.drop_table("billing_memberships")
