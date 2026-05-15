"""phase 14-1 admin role and members api

Revision ID: 20260515_1401
Revises: 20260515_0010
Create Date: 2026-05-15 14:01:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260515_1401"
down_revision = "20260515_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """為 users 新增 is_admin 欄位。"""
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("users", "is_admin", server_default=None)


def downgrade() -> None:
    """回滾 users.is_admin 欄位。"""
    op.drop_column("users", "is_admin")
