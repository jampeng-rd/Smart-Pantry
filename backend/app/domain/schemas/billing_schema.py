"""Billing 模組 Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

BillingMode = Literal["one_time", "subscription"]


class BillingMembershipSummary(BaseModel):
    """目前使用者會員狀態摘要。"""

    is_pro: bool
    tier: str
    membership_status: str
    provider: str | None
    billing_mode: BillingMode | None
    started_at: datetime | None
    ended_at: datetime | None


class BillingUpgradeEntryResponseData(BaseModel):
    """升級入口頁所需設定資料。"""

    billing_mode: BillingMode
    upgrade_entry_path: str
    one_time_entry_path: str
    subscription_entry_path: str
    membership: BillingMembershipSummary
    message: str
