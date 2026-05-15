"""Admin 會員管理 Schema。"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminMemberItem(BaseModel):
    """Admin 會員列表單筆資料。"""

    id: int
    email: EmailStr
    display_name: str
    is_admin: bool
    created_at: datetime


class AdminMemberListResponseData(BaseModel):
    """Admin 會員列表回應資料。"""

    items: list[AdminMemberItem]
    page: int
    page_size: int
    total: int
