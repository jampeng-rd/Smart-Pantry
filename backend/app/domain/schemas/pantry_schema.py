"""Pantry 模組 Schema。"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

PantryItemStatus = Literal["normal", "expiring_soon", "expired"]


class PantryItemCreateRequest(BaseModel):
    """新增食材請求資料。"""

    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=40)
    expiration_date: date | None = None
    storage_location: str | None = Field(default=None, max_length=80)
    note: str | None = Field(default=None, max_length=2000)


class PantryItemUpdateRequest(BaseModel):
    """更新食材請求資料。"""

    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=40)
    expiration_date: date | None = None
    storage_location: str | None = Field(default=None, max_length=80)
    note: str | None = Field(default=None, max_length=2000)


class PantryItemData(BaseModel):
    """單一食材回應資料。"""

    id: int
    user_id: int
    name: str
    category: str
    quantity: float
    unit: str
    expiration_date: date | None
    status: PantryItemStatus
    storage_location: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime


class PantryListResponseData(BaseModel):
    """食材列表回應資料。"""

    items: list[PantryItemData]
    page: int
    page_size: int
    total: int
