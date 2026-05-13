"""Settings 到期提醒寄送紀錄查詢測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException

from backend.app.api.dependencies import get_bearer_token
from backend.app.services.profile_settings_service import ProfileSettingsService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int


@dataclass
class FakeDelivery:
    """測試用寄送紀錄資料。"""

    id: int
    user_id: int
    scheduled_date: date
    send_window: str
    reminder_days: str
    item_ids: list[int]
    email_to: str
    status: str
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime


class FakeProfileSettingsRepository:
    """以記憶體模擬 ProfileSettingsRepository。"""

    def __init__(self) -> None:
        """初始化測試資料。"""
        self.users = {1: FakeUser(id=1), 2: FakeUser(id=2)}
        self.deliveries = [
            FakeDelivery(
                id=11,
                user_id=1,
                scheduled_date=date(2026, 5, 13),
                send_window="morning_08",
                reminder_days="1",
                item_ids=[1, 4, 26],
                email_to="user1@example.com",
                status="success",
                sent_at=datetime(2026, 5, 12, 17, 33, 26, 479836, tzinfo=timezone.utc),
                error_message=None,
                created_at=datetime(2026, 5, 12, 17, 33, 26, tzinfo=timezone.utc),
            ),
            FakeDelivery(
                id=10,
                user_id=1,
                scheduled_date=date(2026, 5, 13),
                send_window="evening_17",
                reminder_days="3",
                item_ids=[9],
                email_to="user1@example.com",
                status="failed",
                sent_at=None,
                error_message="fake email provider timeout",
                created_at=datetime(2026, 5, 12, 8, 0, tzinfo=timezone.utc),
            ),
            FakeDelivery(
                id=7,
                user_id=1,
                scheduled_date=date(2026, 5, 11),
                send_window="morning_08",
                reminder_days="none",
                item_ids=[],
                email_to="user1@example.com",
                status="pending",
                sent_at=None,
                error_message=None,
                created_at=datetime(2026, 5, 11, 8, 0, tzinfo=timezone.utc),
            ),
            FakeDelivery(
                id=99,
                user_id=2,
                scheduled_date=date(2026, 5, 13),
                send_window="morning_08",
                reminder_days="1",
                item_ids=[100],
                email_to="user2@example.com",
                status="success",
                sent_at=datetime(2026, 5, 12, 1, 0, tzinfo=timezone.utc),
                error_message=None,
                created_at=datetime(2026, 5, 12, 1, 0, tzinfo=timezone.utc),
            ),
        ]

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        """依 ID 查詢使用者。"""
        return self.users.get(user_id)

    def list_expiration_reminder_deliveries(self, user_id: int, page: int, page_size: int) -> tuple[list[FakeDelivery], int]:
        """回傳分頁寄送紀錄，排序為 created_at/id 由新到舊。"""
        filtered = [row for row in self.deliveries if row.user_id == user_id]
        filtered.sort(key=lambda row: (row.created_at, row.id), reverse=True)
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        return filtered[start:end], total


def test_unauthorized_should_fail_when_missing_token() -> None:
    """未登入時呼叫寄送紀錄 API 應回傳 401。"""
    with pytest.raises(HTTPException) as exc:
        get_bearer_token(authorization=None)
    assert exc.value.status_code == 401


def test_should_only_return_current_user_rows() -> None:
    """使用者只能查詢自己的寄送紀錄。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=1, page_size=10)

    assert len(result.items) == 3
    assert all(item.email_to == "user1@example.com" for item in result.items)


def test_pagination_should_work() -> None:
    """分頁參數應正確切分資料。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=2, page_size=2)

    assert result.page == 2
    assert result.page_size == 2
    assert result.total == 3
    assert [item.id for item in result.items] == [7]


def test_latest_should_be_first() -> None:
    """紀錄排序應為最新在前。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=1, page_size=10)

    assert [item.id for item in result.items] == [11, 10, 7]


def test_item_count_should_equal_item_ids_length() -> None:
    """item_count 應依 item_ids 長度計算。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=1, page_size=10)

    first = result.items[0]
    assert first.item_ids == [1, 4, 26]
    assert first.item_count == 3


def test_failed_delivery_should_return_error_message() -> None:
    """失敗紀錄應回傳錯誤訊息。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=1, page_size=10)

    failed_item = next(item for item in result.items if item.status == "failed")
    assert failed_item.error_message == "fake email provider timeout"


def test_datetime_should_include_timezone() -> None:
    """datetime 序列化結果應包含 timezone。"""
    service = ProfileSettingsService(repository=FakeProfileSettingsRepository())

    result = service.list_expiration_reminder_deliveries(user_id=1, page=1, page_size=10)
    payload = result.model_dump(mode="json")

    created_at = payload["items"][0]["created_at"]
    sent_at = payload["items"][0]["sent_at"]
    assert created_at.endswith("Z") or created_at.endswith("+00:00")
    assert sent_at.endswith("Z") or sent_at.endswith("+00:00")
