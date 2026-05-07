"""Shopping 資料存取層。"""

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from backend.app.domain.models.pantry_item_model import PantryItem
from backend.app.domain.models.shopping_list_item_model import ShoppingListItem
from backend.app.domain.schemas.shopping_schema import ShoppingSortType


class ShoppingRepository:
    """封裝 Shopping 相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def create_item(
        self,
        user_id: int,
        source_pantry_item_id: int | None,
        name: str,
        quantity: float,
        unit: str,
    ) -> ShoppingListItem:
        """建立購物清單項目。"""
        item = ShoppingListItem(
            user_id=user_id,
            source_pantry_item_id=source_pantry_item_id,
            name=name,
            quantity=quantity,
            unit=unit,
            is_purchased=False,
            purchased_at=None,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_items(
        self,
        user_id: int,
        page: int,
        page_size: int,
        is_purchased: bool | None,
        q: str | None,
        sort: ShoppingSortType,
    ) -> tuple[list[ShoppingListItem], int]:
        """依條件查詢使用者購物清單並回傳總筆數。"""
        statement = select(ShoppingListItem).where(ShoppingListItem.user_id == user_id)
        count_statement = select(func.count(ShoppingListItem.id)).where(ShoppingListItem.user_id == user_id)

        if is_purchased is not None:
            statement = statement.where(ShoppingListItem.is_purchased == is_purchased)
            count_statement = count_statement.where(ShoppingListItem.is_purchased == is_purchased)

        if q:
            keyword = f"%{q}%"
            filter_condition = or_(ShoppingListItem.name.ilike(keyword), ShoppingListItem.unit.ilike(keyword))
            statement = statement.where(filter_condition)
            count_statement = count_statement.where(filter_condition)

        if sort == "purchased_at":
            statement = statement.order_by(desc(ShoppingListItem.purchased_at), desc(ShoppingListItem.id))
        else:
            statement = statement.order_by(desc(ShoppingListItem.created_at), desc(ShoppingListItem.id))

        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        items = list(self.db.execute(statement).scalars().all())
        total = int(self.db.execute(count_statement).scalar_one())
        return items, total

    def get_item_by_id_and_user_id(self, item_id: int, user_id: int) -> ShoppingListItem | None:
        """依 item_id 與 user_id 查詢單筆購物清單。"""
        statement = select(ShoppingListItem).where(ShoppingListItem.id == item_id, ShoppingListItem.user_id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def update_item(self, item: ShoppingListItem, fields: dict) -> ShoppingListItem:
        """更新購物清單資料。"""
        for key, value in fields.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: ShoppingListItem) -> None:
        """刪除購物清單資料。"""
        self.db.delete(item)
        self.db.commit()

    def get_pantry_item_by_id_and_user_id(self, pantry_item_id: int, user_id: int) -> PantryItem | None:
        """確認來源 pantry item 是否存在且屬於指定使用者。"""
        statement = select(PantryItem).where(PantryItem.id == pantry_item_id, PantryItem.user_id == user_id)
        return self.db.execute(statement).scalar_one_or_none()
