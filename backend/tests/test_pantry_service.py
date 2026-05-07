"""Pantry 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from backend.app.services.pantry_service import PantryService


@dataclass
class FakePantryItem:
    """測試用食材資料。"""

    id: int
    user_id: int
    name: str
    category: str
    quantity: Decimal
    unit: str
    expiration_date: date | None
    storage_location: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime


class FakePantryRepository:
    """以記憶體模擬 PantryRepository。"""

    def __init__(self) -> None:
        """初始化假資料儲存。"""
        self.items: dict[int, FakePantryItem] = {}
        self._seq = 1

    def create_item(self, user_id: int, name: str, category: str, quantity: float, unit: str, expiration_date, storage_location: str | None, note: str | None) -> FakePantryItem:
        """建立食材。"""
        now = datetime.now(timezone.utc)
        item = FakePantryItem(
            id=self._seq,
            user_id=user_id,
            name=name,
            category=category,
            quantity=Decimal(str(quantity)),
            unit=unit,
            expiration_date=expiration_date,
            storage_location=storage_location,
            note=note,
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
        category: str | None,
        q: str | None,
        sort: str | None,
        status=None,
    ):
        """查詢食材列表。"""
        rows = [item for item in self.items.values() if item.user_id == user_id]
        if category:
            rows = [item for item in rows if item.category == category]
        if q:
            keyword = q.lower()
            rows = [item for item in rows if keyword in item.name.lower() or (item.note and keyword in item.note.lower())]
        if sort == "expiration_date":
            rows.sort(key=lambda item: (item.expiration_date is None, item.expiration_date, item.id))
        else:
            rows.sort(key=lambda item: item.id)

        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total

    def get_item_by_id_and_user_id(self, item_id: int, user_id: int) -> FakePantryItem | None:
        """依 item_id 與 user_id 查詢食材。"""
        item = self.items.get(item_id)
        if item is None or item.user_id != user_id:
            return None
        return item

    def update_item(self, item: FakePantryItem, fields: dict):
        """更新食材。"""
        for key, value in fields.items():
            setattr(item, key, value)
        item.updated_at = datetime.now(timezone.utc)
        return item

    def delete_item(self, item: FakePantryItem) -> None:
        """刪除食材。"""
        self.items.pop(item.id, None)


@pytest.fixture
def pantry_service() -> tuple[PantryService, FakePantryRepository]:
    """建立 PantryService 與假 repository。"""
    repository = FakePantryRepository()
    return PantryService(pantry_repository=repository), repository


def test_create_pantry_item_success(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """新增食材成功。"""
    service, _ = pantry_service
    result = service.create_item(1, "雞蛋", "蛋類", 10, "顆", date(2026, 5, 20), "fridge", "全聯")
    assert result.user_id == 1
    assert result.name == "雞蛋"


def test_list_only_own_items(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """僅可查詢自己的食材。"""
    service, _ = pantry_service
    service.create_item(1, "雞蛋", "蛋類", 10, "顆", None, None, None)
    service.create_item(2, "牛奶", "乳品", 1, "瓶", None, None, None)

    result = service.list_items(user_id=1, page=1, page_size=20, category=None, q=None, sort=None, status=None)
    assert result.total == 1
    assert result.items[0].name == "雞蛋"


def test_pagination(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """應支援 pagination。"""
    service, _ = pantry_service
    for index in range(1, 6):
        service.create_item(1, f"食材{index}", "雜貨", 1, "包", None, None, None)

    result = service.list_items(user_id=1, page=2, page_size=2, category=None, q=None, sort=None, status=None)
    assert result.total == 5
    assert len(result.items) == 2
    assert result.items[0].name == "食材3"


def test_category_filter(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """應支援 category 篩選。"""
    service, _ = pantry_service
    service.create_item(1, "雞蛋", "蛋類", 10, "顆", None, None, None)
    service.create_item(1, "菠菜", "蔬菜", 1, "把", None, None, None)

    result = service.list_items(user_id=1, page=1, page_size=20, category="蔬菜", q=None, sort=None, status=None)
    assert result.total == 1
    assert result.items[0].name == "菠菜"


def test_q_search(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """應支援 q 搜尋。"""
    service, _ = pantry_service
    service.create_item(1, "高麗菜", "蔬菜", 1, "顆", None, None, "料理用")
    service.create_item(1, "蘋果", "水果", 3, "顆", None, None, None)

    result = service.list_items(user_id=1, page=1, page_size=20, category=None, q="高麗", sort=None, status=None)
    assert result.total == 1
    assert result.items[0].name == "高麗菜"


def test_update_item_success(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """更新食材成功。"""
    service, _ = pantry_service
    item = service.create_item(1, "雞蛋", "蛋類", 10, "顆", None, None, None)

    updated = service.update_item(user_id=1, item_id=item.id, update_fields={"quantity": 8, "note": "已使用"})
    assert updated.quantity == 8
    assert updated.note == "已使用"


def test_delete_item_success(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """刪除食材成功。"""
    service, _ = pantry_service
    item = service.create_item(1, "雞蛋", "蛋類", 10, "顆", None, None, None)

    service.delete_item(user_id=1, item_id=item.id)
    result = service.list_items(user_id=1, page=1, page_size=20, category=None, q=None, sort=None, status=None)
    assert result.total == 0


def test_cannot_operate_other_user_item(pantry_service: tuple[PantryService, FakePantryRepository]) -> None:
    """不可操作其他使用者食材。"""
    service, _ = pantry_service
    item = service.create_item(1, "雞蛋", "蛋類", 10, "顆", None, None, None)

    with pytest.raises(HTTPException) as update_exc:
        service.update_item(user_id=2, item_id=item.id, update_fields={"name": "鴨蛋"})
    assert update_exc.value.status_code == 404

    with pytest.raises(HTTPException) as delete_exc:
        service.delete_item(user_id=2, item_id=item.id)
    assert delete_exc.value.status_code == 404
