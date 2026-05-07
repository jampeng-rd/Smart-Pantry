"""Expiration 與狀態篩選測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backend.app.services.expiration_service import ExpirationService
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
    """支援狀態查詢的假 repository。"""

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

    def list_items(self, user_id: int, page: int, page_size: int, category: str | None, q: str | None, sort: str | None, status=None):
        """查詢食材列表。"""
        rows = [item for item in self.items.values() if item.user_id == user_id]
        if category:
            rows = [item for item in rows if item.category == category]
        if q:
            keyword = q.lower()
            rows = [item for item in rows if keyword in item.name.lower() or (item.note and keyword in item.note.lower())]
        if status:
            rows = [item for item in rows if self._item_status(item.expiration_date) == status]
        if sort == "expiration_date":
            rows.sort(key=lambda item: (item.expiration_date is None, item.expiration_date, item.id))
        else:
            rows.sort(key=lambda item: item.id)
        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total

    def get_item_by_id_and_user_id(self, item_id: int, user_id: int):
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

    def count_items_by_status(self, user_id: int, status: str) -> int:
        """計算狀態數量。"""
        return len([item for item in self.items.values() if item.user_id == user_id and self._item_status(item.expiration_date) == status])

    def list_items_by_status_limited(self, user_id: int, status: str, limit: int, sort: str | None):
        """依狀態回傳限制筆數。"""
        rows = [item for item in self.items.values() if item.user_id == user_id and self._item_status(item.expiration_date) == status]
        if sort == "expiration_date":
            rows.sort(key=lambda item: (item.expiration_date is None, item.expiration_date, item.id))
        else:
            rows.sort(key=lambda item: item.id)
        return rows[:limit]

    @staticmethod
    def _item_status(expiration_date_value: date | None) -> str:
        """依日期計算狀態。"""
        if expiration_date_value is None:
            return "normal"
        today = date.today()
        soon_end = today + timedelta(days=7)
        if expiration_date_value < today:
            return "expired"
        if today <= expiration_date_value <= soon_end:
            return "expiring_soon"
        return "normal"


@pytest.fixture
def services() -> tuple[PantryService, ExpirationService]:
    """建立 Pantry 與 Expiration 服務。"""
    repository = FakePantryRepository()
    pantry_service = PantryService(pantry_repository=repository)
    expiration_service = ExpirationService(pantry_service=pantry_service)
    return pantry_service, expiration_service


def test_expired_status_rule(services: tuple[PantryService, ExpirationService]) -> None:
    """expired 判斷測試。"""
    pantry_service, _ = services
    assert pantry_service.get_item_status(date.today() - timedelta(days=1)) == "expired"


def test_expiring_soon_status_rule(services: tuple[PantryService, ExpirationService]) -> None:
    """expiring_soon 判斷測試。"""
    pantry_service, _ = services
    assert pantry_service.get_item_status(date.today() + timedelta(days=3)) == "expiring_soon"


def test_normal_status_rule(services: tuple[PantryService, ExpirationService]) -> None:
    """normal 判斷測試。"""
    pantry_service, _ = services
    assert pantry_service.get_item_status(date.today() + timedelta(days=8)) == "normal"


def test_null_expiration_is_normal(services: tuple[PantryService, ExpirationService]) -> None:
    """expiration_date 為 null 應視為 normal。"""
    pantry_service, _ = services
    assert pantry_service.get_item_status(None) == "normal"


def test_list_status_expired(services: tuple[PantryService, ExpirationService]) -> None:
    """GET /pantry/items?status=expired 對應邏輯測試。"""
    pantry_service, _ = services
    pantry_service.create_item(1, "過期牛奶", "乳品", 1, "瓶", date.today() - timedelta(days=1), None, None)
    pantry_service.create_item(1, "新鮮牛奶", "乳品", 1, "瓶", date.today() + timedelta(days=9), None, None)
    result = pantry_service.list_items(1, 1, 20, None, None, None, "expired")
    assert result.total == 1
    assert result.items[0].status == "expired"


def test_list_status_expiring_soon(services: tuple[PantryService, ExpirationService]) -> None:
    """GET /pantry/items?status=expiring_soon 對應邏輯測試。"""
    pantry_service, _ = services
    pantry_service.create_item(1, "豆腐", "豆製品", 1, "盒", date.today() + timedelta(days=2), None, None)
    pantry_service.create_item(1, "冷凍肉", "肉類", 1, "包", date.today() + timedelta(days=12), None, None)
    result = pantry_service.list_items(1, 1, 20, None, None, None, "expiring_soon")
    assert result.total == 1
    assert result.items[0].status == "expiring_soon"


def test_list_status_normal(services: tuple[PantryService, ExpirationService]) -> None:
    """GET /pantry/items?status=normal 對應邏輯測試。"""
    pantry_service, _ = services
    pantry_service.create_item(1, "米", "雜糧", 1, "包", None, None, None)
    pantry_service.create_item(1, "優格", "乳品", 1, "盒", date.today() + timedelta(days=2), None, None)
    result = pantry_service.list_items(1, 1, 20, None, None, None, "normal")
    assert result.total == 1
    assert result.items[0].status == "normal"


def test_summary_count_and_items(services: tuple[PantryService, ExpirationService]) -> None:
    """/expiration/summary 應回傳正確 count 與 items。"""
    pantry_service, expiration_service = services
    pantry_service.create_item(1, "過期蛋", "蛋類", 2, "顆", date.today() - timedelta(days=1), None, None)
    pantry_service.create_item(1, "快過期豆腐", "豆製品", 1, "盒", date.today() + timedelta(days=3), None, None)
    pantry_service.create_item(1, "米", "雜糧", 1, "包", None, None, None)

    summary = expiration_service.get_summary(user_id=1, items_limit=10)
    assert summary.expired_count == 1
    assert summary.expiring_soon_count == 1
    assert len(summary.expired_items) == 1
    assert len(summary.expiring_soon_items) == 1


def test_summary_should_not_include_other_users_items(services: tuple[PantryService, ExpirationService]) -> None:
    """不可看到其他使用者的 summary。"""
    pantry_service, expiration_service = services
    pantry_service.create_item(1, "自己的過期蛋", "蛋類", 2, "顆", date.today() - timedelta(days=1), None, None)
    pantry_service.create_item(2, "他人的過期蛋", "蛋類", 2, "顆", date.today() - timedelta(days=1), None, None)

    summary = expiration_service.get_summary(user_id=1, items_limit=10)
    assert summary.expired_count == 1
    assert summary.expired_items[0].name == "自己的過期蛋"


def test_summary_unauthorized_dependency() -> None:
    """未登入不可查 summary（授權依賴）。"""
    from fastapi import HTTPException

    from backend.app.api.dependencies import get_bearer_token

    with pytest.raises(HTTPException) as exc:
        get_bearer_token(authorization=None)
    assert exc.value.status_code == 401
