"""Shopping 商業邏輯服務。"""

from datetime import datetime

from fastapi import HTTPException, status

from backend.app.domain.schemas.shopping_schema import ShoppingItemData, ShoppingListResponseData, ShoppingSortType
from backend.app.infra.repository.shopping_repository import ShoppingRepository


class ShoppingService:
    """處理購物清單 CRUD 與查詢。"""

    def __init__(self, shopping_repository: ShoppingRepository):
        """建立 Shopping 服務實例。"""
        self.shopping_repository = shopping_repository

    def create_item(
        self,
        user_id: int,
        source_pantry_item_id: int | None,
        name: str,
        quantity: float,
        unit: str,
    ) -> ShoppingItemData:
        """新增購物清單項目。"""
        if source_pantry_item_id is not None:
            pantry_item = self.shopping_repository.get_pantry_item_by_id_and_user_id(
                pantry_item_id=source_pantry_item_id,
                user_id=user_id,
            )
            if pantry_item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到對應的 pantry item")

        item = self.shopping_repository.create_item(
            user_id=user_id,
            source_pantry_item_id=source_pantry_item_id,
            name=name,
            quantity=quantity,
            unit=unit,
        )
        return self._to_item_data(item)

    def list_items(
        self,
        user_id: int,
        page: int,
        page_size: int,
        is_purchased: bool | None,
        q: str | None,
        sort: ShoppingSortType,
    ) -> ShoppingListResponseData:
        """查詢目前使用者購物清單（含 pagination）。"""
        items, total = self.shopping_repository.list_items(
            user_id=user_id,
            page=page,
            page_size=page_size,
            is_purchased=is_purchased,
            q=q,
            sort=sort,
        )
        return ShoppingListResponseData(
            items=[self._to_item_data(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
        )

    def update_item(self, user_id: int, item_id: int, update_fields: dict) -> ShoppingItemData:
        """更新目前使用者購物清單項目。"""
        item = self.shopping_repository.get_item_by_id_and_user_id(item_id=item_id, user_id=user_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到購物清單項目")

        sanitized_fields = {key: value for key, value in update_fields.items() if value is not None}
        if not sanitized_fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供可更新欄位")

        if "is_purchased" in sanitized_fields:
            next_value = sanitized_fields["is_purchased"]
            prev_value = item.is_purchased
            if prev_value is False and next_value is True:
                sanitized_fields["purchased_at"] = datetime.utcnow()
            elif prev_value is True and next_value is False:
                sanitized_fields["purchased_at"] = None

        updated = self.shopping_repository.update_item(item=item, fields=sanitized_fields)
        return self._to_item_data(updated)

    def delete_item(self, user_id: int, item_id: int) -> None:
        """刪除目前使用者購物清單項目。"""
        item = self.shopping_repository.get_item_by_id_and_user_id(item_id=item_id, user_id=user_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到購物清單項目")
        self.shopping_repository.delete_item(item=item)

    def _to_item_data(self, item) -> ShoppingItemData:
        """將 model 轉為回應 schema。"""
        return ShoppingItemData(
            id=item.id,
            user_id=item.user_id,
            source_pantry_item_id=item.source_pantry_item_id,
            name=item.name,
            quantity=float(item.quantity),
            unit=item.unit,
            is_purchased=item.is_purchased,
            purchased_at=item.purchased_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
