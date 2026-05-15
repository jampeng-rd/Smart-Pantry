"""Admin 會員管理服務測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.app.services.admin_member_service import AdminMemberService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int
    email: str
    password_hash: str
    display_name: str
    is_admin: bool
    created_at: datetime


class FakeAdminMemberRepository:
    """以記憶體模擬 AdminMemberRepository。"""

    def __init__(self) -> None:
        """初始化資料。"""
        now = datetime.now(timezone.utc)
        self.users: dict[int, FakeUser] = {
            1: FakeUser(
                id=1,
                email="admin@example.com",
                password_hash="hashed-1",
                display_name="管理員",
                is_admin=True,
                created_at=now,
            ),
            2: FakeUser(
                id=2,
                email="user@example.com",
                password_hash="hashed-2",
                display_name="一般會員",
                is_admin=False,
                created_at=now - timedelta(hours=1),
            ),
        }

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        """依 ID 查詢使用者。"""
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> FakeUser | None:
        """依 Email 查詢使用者。"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def create_user(self, email: str, password_hash: str, display_name: str, is_admin: bool) -> FakeUser:
        """建立新使用者。"""
        next_id = max(self.users.keys(), default=0) + 1
        user = FakeUser(
            id=next_id,
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            is_admin=is_admin,
            created_at=datetime.now(timezone.utc),
        )
        self.users[user.id] = user
        return user

    def save_user(self, user: FakeUser) -> FakeUser:
        """儲存使用者。"""
        self.users[user.id] = user
        return user

    def list_members(self, page: int, page_size: int, q: str | None = None) -> tuple[list[FakeUser], int]:
        """分頁查詢使用者（ID 由小到大），支援關鍵字搜尋。"""
        rows = sorted(self.users.values(), key=lambda user: user.id)
        keyword = (q or "").strip().lower()
        if keyword:
            rows = [row for row in rows if keyword in row.display_name.lower() or keyword in row.email.lower()]
        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total


@pytest.fixture
def admin_service() -> tuple[AdminMemberService, FakeAdminMemberRepository]:
    """建立 AdminMemberService 測試實例。"""
    repository = FakeAdminMemberRepository()
    return AdminMemberService(repository=repository), repository


def test_ensure_admin_user_should_pass_for_admin(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """admin 使用者應可通過權限檢查。"""
    service, _ = admin_service
    service.ensure_admin_user(user_id=1)


def test_ensure_admin_user_should_reject_non_admin(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """非 admin 使用者應被拒絕。"""
    service, _ = admin_service
    with pytest.raises(HTTPException) as exc:
        service.ensure_admin_user(user_id=2)
    assert exc.value.status_code == 403


def test_list_members_should_return_member_list(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """admin 可查詢會員列表。"""
    service, _ = admin_service
    data = service.list_members(page=1, page_size=10)
    assert data.total == 2
    assert len(data.items) == 2
    assert data.items[0].email == "admin@example.com"


def test_list_members_should_support_keyword_search(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """會員列表可依 display_name/email 關鍵字搜尋。"""
    service, _ = admin_service
    data = service.list_members(page=1, page_size=10, q="admin")
    assert data.total == 1
    assert len(data.items) == 1
    assert data.items[0].email == "admin@example.com"


def test_bootstrap_admin_should_upgrade_existing_user(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """既有使用者可升級為 admin。"""
    service, repository = admin_service
    message, changed = service.bootstrap_admin(email="user@example.com")
    assert changed is True
    assert "已將使用者設為 admin" in message
    assert repository.users[2].is_admin is True


def test_bootstrap_admin_should_create_user_when_empty_db_mode(admin_service: tuple[AdminMemberService, FakeAdminMemberRepository]) -> None:
    """空 DB 模式可建立第一個 admin。"""
    service, repository = admin_service
    message, changed = service.bootstrap_admin(
        email="first-admin@example.com",
        create_if_not_exists=True,
        password="password123",
        display_name="第一位管理員",
    )
    assert changed is True
    assert "已建立第一個 admin 帳號" in message

    created_user = repository.get_user_by_email("first-admin@example.com")
    assert created_user is not None
    assert created_user.is_admin is True
