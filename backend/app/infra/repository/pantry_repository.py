"""Pantry 資料存取層。"""

from sqlalchemy import asc, func, or_, select
from sqlalchemy.orm import Session

from backend.app.domain.models.pantry_item_model import PantryItem


class PantryRepository:
    """封裝 Pantry 相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

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
    ) -> PantryItem:
        """建立食材資料。"""
        item = PantryItem(
            user_id=user_id,
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            expiration_date=expiration_date,
            storage_location=storage_location,
            note=note,
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
        category: str | None,
        q: str | None,
        sort: str | None,
    ) -> tuple[list[PantryItem], int]:
        """依條件查詢使用者食材列表並回傳總筆數。"""
        statement = select(PantryItem).where(PantryItem.user_id == user_id)
        count_statement = select(func.count(PantryItem.id)).where(PantryItem.user_id == user_id)

        if category:
            statement = statement.where(PantryItem.category == category)
            count_statement = count_statement.where(PantryItem.category == category)

        if q:
            keyword = f"%{q}%"
            filter_condition = or_(PantryItem.name.ilike(keyword), PantryItem.note.ilike(keyword))
            statement = statement.where(filter_condition)
            count_statement = count_statement.where(filter_condition)

        if sort == "expiration_date":
            statement = statement.order_by(asc(PantryItem.expiration_date), asc(PantryItem.id))
        else:
            statement = statement.order_by(asc(PantryItem.id))

        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        items = list(self.db.execute(statement).scalars().all())
        total = int(self.db.execute(count_statement).scalar_one())
        return items, total

    def get_item_by_id_and_user_id(self, item_id: int, user_id: int) -> PantryItem | None:
        """依 item_id 與 user_id 查詢單筆食材。"""
        statement = select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def update_item(self, item: PantryItem, fields: dict) -> PantryItem:
        """更新食材資料。"""
        for key, value in fields.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: PantryItem) -> None:
        """刪除食材資料。"""
        self.db.delete(item)
        self.db.commit()
