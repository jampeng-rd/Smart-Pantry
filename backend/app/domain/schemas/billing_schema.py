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


class BillingOneTimeCheckoutResponseData(BaseModel):
    """藍新單次付款表單提交資料。"""

    transaction_id: int
    external_trade_no: str
    gateway_url: str
    merchant_id: str
    trade_info: str
    trade_sha: str
    version: str


class BillingTransactionStatusResponseData(BaseModel):
    """單筆交易狀態查詢回應。"""

    external_trade_no: str
    transaction_status: str
    membership_status: str
    is_pro: bool
    amount: float
    paid_at: datetime | None
    failed_at: datetime | None
