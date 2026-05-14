"""phase 12-1 baseline schema

Revision ID: 20260514_1201
Revises:
Create Date: 2026-05-14 23:40:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260514_1201"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """建立 Phase 12-1 baseline schema。"""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_snapshot", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_jobs_created_at", "ai_jobs", ["created_at"], unique=False)
    op.create_index("ix_ai_jobs_job_type", "ai_jobs", ["job_type"], unique=False)
    op.create_index("ix_ai_jobs_status", "ai_jobs", ["status"], unique=False)
    op.create_index("ix_ai_jobs_status_created_at", "ai_jobs", ["status", "created_at"], unique=False)
    op.create_index("ix_ai_jobs_user_id", "ai_jobs", ["user_id"], unique=False)
    op.create_index("ix_ai_jobs_user_id_created_at", "ai_jobs", ["user_id", "created_at"], unique=False)

    op.create_table(
        "pantry_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("storage_location", sa.String(length=80), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pantry_items_category", "pantry_items", ["category"], unique=False)
    op.create_index("ix_pantry_items_expiration_date", "pantry_items", ["expiration_date"], unique=False)
    op.create_index("ix_pantry_items_name", "pantry_items", ["name"], unique=False)
    op.create_index("ix_pantry_items_user_id", "pantry_items", ["user_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("replaced_by_token_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=32), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("expiration_email_reminder_days", sa.String(length=8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"], unique=True)

    op.create_table(
        "expiration_reminder_deliveries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("send_window", sa.String(length=32), nullable=False),
        sa.Column("reminder_days", sa.String(length=8), nullable=False),
        sa.Column("item_ids", sa.JSON(), nullable=False),
        sa.Column("email_to", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("final_status", sa.String(length=32), nullable=False),
        sa.Column("error_category", sa.String(length=64), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expiration_reminder_deliveries_scheduled_date", "expiration_reminder_deliveries", ["scheduled_date"], unique=False)
    op.create_index("ix_expiration_reminder_deliveries_user_id", "expiration_reminder_deliveries", ["user_id"], unique=False)
    op.create_index(
        "ix_expiration_reminder_user_date_window",
        "expiration_reminder_deliveries",
        ["user_id", "scheduled_date", "send_window"],
        unique=False,
    )
    op.create_index("ix_expiration_reminder_status", "expiration_reminder_deliveries", ["status"], unique=False)

    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_pantry_item_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("is_purchased", sa.Boolean(), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_pantry_item_id"], ["pantry_items.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shopping_list_items_is_purchased", "shopping_list_items", ["is_purchased"], unique=False)
    op.create_index("ix_shopping_list_items_user_id", "shopping_list_items", ["user_id"], unique=False)


def downgrade() -> None:
    """回滾 Phase 12-1 baseline schema。"""
    op.drop_index("ix_shopping_list_items_user_id", table_name="shopping_list_items")
    op.drop_index("ix_shopping_list_items_is_purchased", table_name="shopping_list_items")
    op.drop_table("shopping_list_items")

    op.drop_index("ix_expiration_reminder_status", table_name="expiration_reminder_deliveries")
    op.drop_index("ix_expiration_reminder_user_date_window", table_name="expiration_reminder_deliveries")
    op.drop_index("ix_expiration_reminder_deliveries_user_id", table_name="expiration_reminder_deliveries")
    op.drop_index("ix_expiration_reminder_deliveries_scheduled_date", table_name="expiration_reminder_deliveries")
    op.drop_table("expiration_reminder_deliveries")

    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_table("user_preferences")

    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_pantry_items_user_id", table_name="pantry_items")
    op.drop_index("ix_pantry_items_name", table_name="pantry_items")
    op.drop_index("ix_pantry_items_expiration_date", table_name="pantry_items")
    op.drop_index("ix_pantry_items_category", table_name="pantry_items")
    op.drop_table("pantry_items")

    op.drop_index("ix_ai_jobs_user_id_created_at", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_user_id", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_status_created_at", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_status", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_job_type", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_created_at", table_name="ai_jobs")
    op.drop_table("ai_jobs")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
