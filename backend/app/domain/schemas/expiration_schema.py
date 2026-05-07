"""Expiration 模組 Schema。"""

from pydantic import BaseModel

from backend.app.domain.schemas.pantry_schema import PantryItemData


class ExpirationSummaryResponseData(BaseModel):
    """過期提醒摘要回應資料。"""

    expiring_soon_count: int
    expired_count: int
    expiring_soon_items: list[PantryItemData]
    expired_items: list[PantryItemData]
