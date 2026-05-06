"""Pantry 商業邏輯服務。"""

from fastapi import HTTPException, status

from backend.app.domain.schemas.pantry_schema import PantryItemData, PantryListResponseData
from backend.app.infra.repository.pantry_repository import PantryRepository


class PantryService:
    """處理食材庫存 CRUD 與查詢。"""

    def __init__(self, pantry_repository: PantryRepository):
        """建立 Pantry 服務實例。"""
        self.pantry_repository = pantry_repository

    def create_item(
        self,
        user_id: int,
        name: str,
        category: str,
        quantity: float,
        unit: str,
        expiration_date,
        storage_location: str | None,
        note: str | None,
    ) -> PantryItemData:
        """新增食材。"""
        item = self.pantry_repository.create_item(
            user_id=user_id,
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            expiration_date=expiration_date,
            storage_location=storage_location,
            note=note,
        )
        return self._to_item_data(item)

    def list_items(
        self,
        user_id: int,
        page: int,
        page_size: int,
        category: str | None,
        q: str | None,
        sort: str | None,
    ) -> PantryListResponseData:
        """查詢目前使用者食材（含 pagination）。"""
        items, total = self.pantry_repository.list_items(
            user_id=user_id,
            page=page,
            page_size=page_size,
            category=category,
            q=q,
            sort=sort,
        )
        return PantryListResponseData(
            items=[self._to_item_data(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
        )

    def update_item(self, user_id: int, item_id: int, update_fields: dict) -> PantryItemData:
        """更新目前使用者食材。"""
        item = self.pantry_repository.get_item_by_id_and_user_id(item_id=item_id, user_id=user_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到食材資料")

        sanitized_fields = {key: value for key, value in update_fields.items() if value is not None}
        if not sanitized_fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供可更新欄位")

        updated = self.pantry_repository.update_item(item=item, fields=sanitized_fields)
        return self._to_item_data(updated)

    def delete_item(self, user_id: int, item_id: int) -> None:
        """刪除目前使用者食材。"""
        item = self.pantry_repository.get_item_by_id_and_user_id(item_id=item_id, user_id=user_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到食材資料")
        self.pantry_repository.delete_item(item=item)

    def _to_item_data(self, item) -> PantryItemData:
        """將 model 轉為回應 schema。"""
        return PantryItemData(
            id=item.id,
            user_id=item.user_id,
            name=item.name,
            category=item.category,
            quantity=float(item.quantity),
            unit=item.unit,
            expiration_date=item.expiration_date,
            storage_location=item.storage_location,
            note=item.note,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
