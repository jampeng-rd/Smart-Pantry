"""Expiration 商業邏輯服務。"""

from backend.app.domain.schemas.expiration_schema import ExpirationSummaryResponseData
from backend.app.services.pantry_service import PantryService


class ExpirationService:
    """處理食材過期提醒摘要。"""

    def __init__(self, pantry_service: PantryService):
        """建立 Expiration 服務實例。"""
        self.pantry_service = pantry_service

    def get_summary(self, user_id: int, items_limit: int = 10) -> ExpirationSummaryResponseData:
        """取得目前使用者的過期與即將過期摘要。"""
        expired_count = self.pantry_service.count_items_by_status(user_id=user_id, status="expired")
        expiring_soon_count = self.pantry_service.count_items_by_status(user_id=user_id, status="expiring_soon")

        expired_items = self.pantry_service.list_items_by_status_limited(
            user_id=user_id,
            status="expired",
            limit=items_limit,
            sort="expiration_date",
        )
        expiring_soon_items = self.pantry_service.list_items_by_status_limited(
            user_id=user_id,
            status="expiring_soon",
            limit=items_limit,
            sort="expiration_date",
        )

        return ExpirationSummaryResponseData(
            expiring_soon_count=expiring_soon_count,
            expired_count=expired_count,
            expiring_soon_items=expiring_soon_items,
            expired_items=expired_items,
        )
