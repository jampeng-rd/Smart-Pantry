"""Shopping 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from backend.app.services.shopping_service import ShoppingService


@dataclass
class FakePantryItem:
    """測試用 pantry item 資料。"""

    id: int
    user_id: int


@dataclass
class FakeShoppingItem:
    """測試用購物清單資料。"""

    id: int
    user_id: int
    source_pantry_item_id: int | None
    name: str
    quantity: Decimal
    unit: str
    is_purchased: bool
    purchased_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FakeShoppingRepository:
    """以記憶體模擬 ShoppingRepository。"""

    def __init__(self) -> None:
        """初始化假資料儲存。"""
        self.items: dict[int, FakeShoppingItem] = {}
        self.pantry_items: dict[int, FakePantryItem] = {}
        self._seq = 1

    def seed_pantry_item(self, pantry_item_id: int, user_id: int) -> None:
        """建立假 pantry item。"""
        self.pantry_items[pantry_item_id] = FakePantryItem(id=pantry_item_id, user_id=user_id)

    def get_pantry_item_by_id_and_user_id(self, pantry_item_id: int, user_id: int) -> FakePantryItem | None:
        """依 id 與 user_id 查詢 pantry item。"""
        item = self.pantry_items.get(pantry_item_id)
        if item is None or item.user_id != user_id:
            return None
        return item

    def create_item(self, user_id: int, source_pantry_item_id: int | None, name: str, quantity: float, unit: str) -> FakeShoppingItem:
        """建立購物清單項目。"""
        now = datetime.now(timezone.utc)
        item = FakeShoppingItem(
            id=self._seq,
            user_id=user_id,
            source_pantry_item_id=source_pantry_item_id,
            name=name,
            quantity=Decimal(str(quantity)),
            unit=unit,
            is_purchased=False,
            purchased_at=None,
            created_at=now,
            updated_at=now,
        )
        self.items[item.id] = item
        self._seq += 1
        return item

    def list_items(
        self,
        user_id: int,
        page: int,
        page_size: int,
        is_purchased: bool | None,
        q: str | None,
        sort: str,
    ):
        """查詢購物清單。"""
        rows = [item for item in self.items.values() if item.user_id == user_id]

        if is_purchased is not None:
            rows = [item for item in rows if item.is_purchased is is_purchased]

        if q:
            keyword = q.lower()
            rows = [item for item in rows if keyword in item.name.lower() or keyword in item.unit.lower()]

        if sort == "purchased_at":
            rows.sort(key=lambda item: (item.purchased_at is not None, item.purchased_at, item.id), reverse=True)
        else:
            rows.sort(key=lambda item: (item.created_at, item.id), reverse=True)

        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total

    def get_item_by_id_and_user_id(self, item_id: int, user_id: int) -> FakeShoppingItem | None:
        """依 item_id 與 user_id 查詢購物清單。"""
        item = self.items.get(item_id)
        if item is None or item.user_id != user_id:
            return None
        return item

    def update_item(self, item: FakeShoppingItem, fields: dict):
        """更新購物清單。"""
        for key, value in fields.items():
            setattr(item, key, value)
        item.updated_at = datetime.now(timezone.utc)
        return item

    def delete_item(self, item: FakeShoppingItem) -> None:
        """刪除購物清單。"""
        self.items.pop(item.id, None)


@pytest.fixture
def shopping_service() -> tuple[ShoppingService, FakeShoppingRepository]:
    """建立 ShoppingService 與假 repository。"""
    repository = FakeShoppingRepository()
    return ShoppingService(shopping_repository=repository), repository


def test_create_shopping_item_manual_success(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """手動新增 shopping item 成功。"""
    service, _ = shopping_service

    result = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")

    assert result.user_id == 1
    assert result.name == "牛奶"
    assert result.source_pantry_item_id is None
    assert result.created_at.tzinfo is not None
    assert result.updated_at.tzinfo is not None


def test_create_shopping_item_from_pantry_success(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """從 pantry item 新增 shopping item 成功。"""
    service, repository = shopping_service
    repository.seed_pantry_item(pantry_item_id=12, user_id=1)

    result = service.create_item(user_id=1, source_pantry_item_id=12, name="牛奶", quantity=1, unit="瓶")

    assert result.source_pantry_item_id == 12


def test_create_shopping_item_fail_when_source_pantry_not_found(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """source_pantry_item_id 不存在應失敗。"""
    service, _ = shopping_service

    with pytest.raises(HTTPException) as exc:
        service.create_item(user_id=1, source_pantry_item_id=999, name="牛奶", quantity=1, unit="瓶")

    assert exc.value.status_code == 404


def test_create_shopping_item_fail_when_source_pantry_other_user(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """source_pantry_item_id 屬於其他使用者應失敗。"""
    service, repository = shopping_service
    repository.seed_pantry_item(pantry_item_id=12, user_id=2)

    with pytest.raises(HTTPException) as exc:
        service.create_item(user_id=1, source_pantry_item_id=12, name="牛奶", quantity=1, unit="瓶")

    assert exc.value.status_code == 404


def test_list_only_own_shopping_items(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """僅可查詢自己的 shopping list。"""
    service, _ = shopping_service
    service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")
    service.create_item(user_id=2, source_pantry_item_id=None, name="雞蛋", quantity=1, unit="盒")

    result = service.list_items(user_id=1, page=1, page_size=20, is_purchased=None, q=None, sort="created_at")

    assert result.total == 1
    assert result.items[0].name == "牛奶"


def test_pagination(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """應支援 pagination。"""
    service, _ = shopping_service
    for index in range(1, 6):
        service.create_item(user_id=1, source_pantry_item_id=None, name=f"食材{index}", quantity=1, unit="包")

    result = service.list_items(user_id=1, page=2, page_size=2, is_purchased=None, q=None, sort="created_at")

    assert result.total == 5
    assert len(result.items) == 2


def test_is_purchased_filter(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """應支援 is_purchased 篩選。"""
    service, _ = shopping_service
    item1 = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")
    service.create_item(user_id=1, source_pantry_item_id=None, name="雞蛋", quantity=1, unit="盒")
    service.update_item(user_id=1, item_id=item1.id, update_fields={"is_purchased": True})

    result = service.list_items(user_id=1, page=1, page_size=20, is_purchased=True, q=None, sort="created_at")

    assert result.total == 1
    assert result.items[0].name == "牛奶"


def test_q_search(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """應支援 q 搜尋。"""
    service, _ = shopping_service
    service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")
    service.create_item(user_id=1, source_pantry_item_id=None, name="雞蛋", quantity=1, unit="盒")

    result = service.list_items(user_id=1, page=1, page_size=20, is_purchased=None, q="牛", sort="created_at")

    assert result.total == 1
    assert result.items[0].name == "牛奶"


def test_set_purchased_should_auto_set_purchased_at(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """標記已購買時應自動設定 purchased_at。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")

    updated = service.update_item(user_id=1, item_id=item.id, update_fields={"is_purchased": True})
    payload = updated.model_dump(mode="json")

    assert updated.is_purchased is True
    assert updated.purchased_at is not None
    assert updated.purchased_at.tzinfo is not None
    assert payload["purchased_at"].endswith("Z") or payload["purchased_at"].endswith("+00:00")


def test_unset_purchased_should_clear_purchased_at(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """取消已購買時應清空 purchased_at。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")
    service.update_item(user_id=1, item_id=item.id, update_fields={"is_purchased": True})

    updated = service.update_item(user_id=1, item_id=item.id, update_fields={"is_purchased": False})

    assert updated.is_purchased is False
    assert updated.purchased_at is None


def test_datetime_json_should_include_timezone(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """datetime 序列化應包含 timezone。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")
    payload = item.model_dump(mode="json")

    assert payload["created_at"].endswith("Z") or payload["created_at"].endswith("+00:00")
    assert payload["updated_at"].endswith("Z") or payload["updated_at"].endswith("+00:00")


def test_update_shopping_item_success(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """更新 shopping item 成功。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")

    updated = service.update_item(user_id=1, item_id=item.id, update_fields={"name": "低脂牛奶", "quantity": 2})

    assert updated.name == "低脂牛奶"
    assert updated.quantity == 2


def test_delete_shopping_item_success(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """刪除 shopping item 成功。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")

    service.delete_item(user_id=1, item_id=item.id)
    result = service.list_items(user_id=1, page=1, page_size=20, is_purchased=None, q=None, sort="created_at")

    assert result.total == 0


def test_cannot_operate_other_user_shopping_item(shopping_service: tuple[ShoppingService, FakeShoppingRepository]) -> None:
    """不可查詢、更新、刪除其他使用者 shopping item。"""
    service, _ = shopping_service
    item = service.create_item(user_id=1, source_pantry_item_id=None, name="牛奶", quantity=1, unit="瓶")

    other_user_list = service.list_items(user_id=2, page=1, page_size=20, is_purchased=None, q=None, sort="created_at")
    assert other_user_list.total == 0

    with pytest.raises(HTTPException) as update_exc:
        service.update_item(user_id=2, item_id=item.id, update_fields={"name": "不可更新"})
    assert update_exc.value.status_code == 404

    with pytest.raises(HTTPException) as delete_exc:
        service.delete_item(user_id=2, item_id=item.id)
    assert delete_exc.value.status_code == 404
