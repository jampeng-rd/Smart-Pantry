"""Auth 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.app.infra.security import create_access_token, hash_password
from backend.app.services.auth_service import AuthService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int
    email: str
    password_hash: str
    display_name: str


@dataclass
class FakeRefreshToken:
    """測試用 refresh token 資料。"""

    id: int
    token_hash: str
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None = None
    replaced_by_token_id: int | None = None


class FakeAuthRepository:
    """以記憶體模擬 AuthRepository。"""

    def __init__(self) -> None:
        """初始化假資料儲存。"""
        self.users_by_id: dict[int, FakeUser] = {}
        self.users_by_email: dict[str, FakeUser] = {}
        self.tokens_by_hash: dict[str, FakeRefreshToken] = {}
        self._user_seq = 1
        self._token_seq = 1

    def get_user_by_email(self, email: str) -> FakeUser | None:
        """依 email 取得使用者。"""
        return self.users_by_email.get(email)

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        """依 ID 取得使用者。"""
        return self.users_by_id.get(user_id)

    def create_user(self, email: str, password_hash: str, display_name: str) -> FakeUser:
        """建立使用者。"""
        user = FakeUser(id=self._user_seq, email=email, password_hash=password_hash, display_name=display_name)
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        self._user_seq += 1
        return user

    def create_refresh_token(self, token_hash: str, user_id: int, expires_at: datetime) -> FakeRefreshToken:
        """建立 refresh token。"""
        row = FakeRefreshToken(id=self._token_seq, token_hash=token_hash, user_id=user_id, expires_at=expires_at)
        self.tokens_by_hash[token_hash] = row
        self._token_seq += 1
        return row

    def get_refresh_token_by_hash(self, token_hash: str) -> FakeRefreshToken | None:
        """依 hash 取得 refresh token。"""
        return self.tokens_by_hash.get(token_hash)

    def revoke_refresh_token(self, token_row: FakeRefreshToken) -> None:
        """撤銷 refresh token。"""
        token_row.revoked_at = datetime.now(timezone.utc)

    def revoke_refresh_token_with_replacement(self, token_row: FakeRefreshToken, replacement_id: int) -> None:
        """撤銷舊 token 並更新 replacement。"""
        token_row.revoked_at = datetime.now(timezone.utc)
        token_row.replaced_by_token_id = replacement_id


@pytest.fixture
def auth_service() -> tuple[AuthService, FakeAuthRepository]:
    """建立 AuthService 與假 repository。"""
    repository = FakeAuthRepository()
    return AuthService(auth_repository=repository), repository


def test_register_success(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """註冊成功應回傳使用者資訊。"""
    service, _ = auth_service
    result = service.register("user@example.com", "password123", "測試者")
    assert result.user.email == "user@example.com"


def test_register_duplicate_email(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """重複 email 註冊應失敗。"""
    service, _ = auth_service
    service.register("user@example.com", "password123", "測試者")
    with pytest.raises(HTTPException) as exc:
        service.register("user@example.com", "password123", "測試者2")
    assert exc.value.status_code == 400


def test_login_success(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """登入成功應回傳 access 與 refresh token。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")
    result = service.login("user@example.com", "password123")
    assert result.token_type == "bearer"
    assert result.access_token
    assert result.refresh_token


def test_login_wrong_password(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """密碼錯誤應回傳 401。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")
    with pytest.raises(HTTPException) as exc:
        service.login("user@example.com", "wrong-password")
    assert exc.value.status_code == 401


def test_refresh_success(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """refresh 成功應回傳新 token 並撤銷舊 token。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")
    login_result = service.login("user@example.com", "password123")

    refresh_result = service.refresh(login_result.refresh_token)
    assert refresh_result.access_token
    assert refresh_result.refresh_token != login_result.refresh_token


def test_refresh_token_expired(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """refresh token 過期應失敗。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")
    login_result = service.login("user@example.com", "password123")

    from backend.app.infra.security import hash_refresh_token

    row = repository.get_refresh_token_by_hash(hash_refresh_token(login_result.refresh_token))
    assert row is not None
    row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    with pytest.raises(HTTPException) as exc:
        service.refresh(login_result.refresh_token)
    assert exc.value.status_code == 401


def test_logout_then_refresh_failed(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """登出後 refresh token 應無法使用。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")
    login_result = service.login("user@example.com", "password123")
    service.logout(login_result.refresh_token)

    with pytest.raises(HTTPException) as exc:
        service.refresh(login_result.refresh_token)
    assert exc.value.status_code == 401


def test_auth_me_success(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """/auth/me 成功情境。"""
    service, repository = auth_service
    user = repository.create_user("user@example.com", hash_password("password123"), "測試者")
    access_token, _ = create_access_token(user_id=user.id, email=user.email)

    result = service.get_me(access_token)
    assert result.user.id == user.id


def test_auth_me_unauthorized(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """/auth/me 未登入應失敗。"""
    service, _ = auth_service
    invalid_access_token, _ = create_access_token(user_id=999, email="ghost@example.com")

    with pytest.raises(HTTPException) as exc:
        service.get_me(invalid_access_token)
    assert exc.value.status_code == 401
