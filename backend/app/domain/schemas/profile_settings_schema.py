"""Profile 與 Settings 模組 Schema。"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

ThemeMode = Literal["light-soft", "dark-soft"]
ReminderDays = Literal["none", "1", "3"]


class ProfileResponseData(BaseModel):
    """個人資料回應資料。"""

    display_name: str
    email: str
    avatar_url: str | None
    avatar_fallback: str


class ProfileUpdateRequest(BaseModel):
    """更新個人資料請求。"""

    display_name: str = Field(min_length=1, max_length=120)


class ChangePasswordRequest(BaseModel):
    """修改密碼請求。"""

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class SettingsResponseData(BaseModel):
    """設定回應資料。"""

    theme: ThemeMode
    timezone: str | None
    language: str
    expiration_email_reminder_days: ReminderDays


class SettingsUpdateRequest(BaseModel):
    """更新設定請求。"""

    theme: ThemeMode | None = None
    timezone: str | None = None
    expiration_email_reminder_days: ReminderDays | None = None
    language: str | None = None


class ExpirationReminderDeliveryItem(BaseModel):
    """到期提醒寄送紀錄單筆資料。"""

    id: int
    scheduled_date: date
    send_window: str
    reminder_days: ReminderDays
    item_ids: list[int]
    item_count: int
    email_to: str
    status: str
    final_status: str
    attempt_count: int
    last_error_message: str | None
    last_attempt_at: datetime | None
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime


class ExpirationReminderDeliveryListResponseData(BaseModel):
    """到期提醒寄送紀錄列表回應資料。"""

    items: list[ExpirationReminderDeliveryItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=50)
    total: int = Field(ge=0)
