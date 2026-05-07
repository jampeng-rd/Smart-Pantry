"""Shopping 模組 Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ShoppingSortType = Literal["created_at", "purchased_at"]


class ShoppingItemCreateRequest(BaseModel):
    """新增購物清單項目請求資料。"""

    source_pantry_item_id: int | None = Field(default=None, ge=1)
    name: str = Field(min_length=1, max_length=160)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=40)


class ShoppingItemUpdateRequest(BaseModel):
    """更新購物清單項目請求資料。"""

    name: str | None = Field(default=None, min_length=1, max_length=160)
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=40)
    is_purchased: bool | None = None


class ShoppingItemData(BaseModel):
    """單一購物清單項目回應資料。"""

    id: int
    user_id: int
    source_pantry_item_id: int | None
    name: str
    quantity: float
    unit: str
    is_purchased: bool
    purchased_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ShoppingListResponseData(BaseModel):
    """購物清單列表回應資料。"""

    items: list[ShoppingItemData]
    page: int
    page_size: int
    total: int
