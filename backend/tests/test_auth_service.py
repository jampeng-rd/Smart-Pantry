"""Auth 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.app.infra.security import create_access_token, hash_password
from backend.app.infra.email_client import EmailMessage, EmailSendResult
from backend.app.infra.settings import Settings
from backend.app.services.auth_service import AuthService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int
    email: str
    password_hash: str
    display_name: str
    is_admin: bool = False


@dataclass
class FakeRefreshToken:
    """測試用 refresh token 資料。"""

    id: int
    token_hash: str
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None = None
    replaced_by_token_id: int | None = None


@dataclass
class FakePasswordResetToken:
    """測試用重設密碼 token 資料。"""

    id: int
    user_id: int
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None


class FakeAuthRepository:
    """以記憶體模擬 AuthRepository。"""

    def __init__(self) -> None:
        """初始化假資料儲存。"""
        self.users_by_id: dict[int, FakeUser] = {}
        self.users_by_email: dict[str, FakeUser] = {}
        self.tokens_by_hash: dict[str, FakeRefreshToken] = {}
        self._user_seq = 1
        self._token_seq = 1
        self.password_reset_tokens_by_hash: dict[str, FakePasswordResetToken] = {}
        self._password_reset_seq = 1

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

    def revoke_all_active_refresh_tokens_by_user_id(self, user_id: int) -> None:
        """撤銷使用者所有有效 refresh token。"""
        now = datetime.now(timezone.utc)
        for token in self.tokens_by_hash.values():
            if token.user_id == user_id and token.revoked_at is None:
                token.revoked_at = now

    def create_password_reset_token(self, user_id: int, token_hash: str, expires_at: datetime) -> FakePasswordResetToken:
        """建立重設密碼 token。"""
        row = FakePasswordResetToken(
            id=self._password_reset_seq,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.password_reset_tokens_by_hash[token_hash] = row
        self._password_reset_seq += 1
        return row

    def get_password_reset_token_by_hash(self, token_hash: str) -> FakePasswordResetToken | None:
        """依 hash 取得重設密碼 token。"""
        return self.password_reset_tokens_by_hash.get(token_hash)

    def mark_password_reset_token_used(self, token_row: FakePasswordResetToken) -> None:
        """標記 token 已使用。"""
        token_row.used_at = datetime.now(timezone.utc)

    def save_user(self, user: FakeUser) -> FakeUser:
        """儲存使用者。"""
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return user


class FakeEmailClient:
    """測試用 fake email client。"""

    def __init__(self) -> None:
        """初始化已寄送信件紀錄。"""
        self.sent_messages: list[EmailMessage] = []

    def send_email(self, message: EmailMessage) -> EmailSendResult:
        """記錄信件並回傳成功。"""
        self.sent_messages.append(message)
        return EmailSendResult(success=True)


@pytest.fixture
def auth_service() -> tuple[AuthService, FakeAuthRepository]:
    """建立 AuthService 與假 repository。"""
    repository = FakeAuthRepository()
    email_client = FakeEmailClient()
    settings = Settings(email_provider="fake")
    return AuthService(auth_repository=repository, email_client=email_client, settings=settings), repository


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

    from backend.app.infra.security import hash_refresh_token

    old_row = repository.get_refresh_token_by_hash(hash_refresh_token(login_result.refresh_token))
    new_row = repository.get_refresh_token_by_hash(hash_refresh_token(refresh_result.refresh_token))
    assert old_row is not None
    assert new_row is not None
    assert old_row.revoked_at is not None
    assert old_row.replaced_by_token_id == new_row.id


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


def test_forgot_password_should_return_same_message_when_user_exists_or_not(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """忘記密碼在存在/不存在 email 時，需回相同成功訊息。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")

    existing_message = service.forgot_password("user@example.com")
    missing_message = service.forgot_password("ghost@example.com")
    assert existing_message == missing_message


def test_forgot_password_should_store_reset_token_hash_only(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """忘記密碼只可儲存 token hash，不可儲存明文。"""
    service, repository = auth_service
    repository.create_user("user@example.com", hash_password("password123"), "測試者")

    service.forgot_password("user@example.com")
    assert len(repository.password_reset_tokens_by_hash) == 1
    token_hash = next(iter(repository.password_reset_tokens_by_hash.keys()))
    assert len(token_hash) == 64
    message = service.email_client.sent_messages[0]
    assert message.content_text.find(token_hash) == -1


def test_reset_password_should_return_friendly_error_when_token_expired(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """重設密碼 token 過期時應回繁中友善錯誤。"""
    service, repository = auth_service
    user = repository.create_user("user@example.com", hash_password("password123"), "測試者")
    raw_token = "expired-token"
    from backend.app.infra.security import hash_password_reset_token

    repository.create_password_reset_token(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw_token),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    with pytest.raises(HTTPException) as exc:
        service.reset_password(raw_token, "new-password-123")
    assert exc.value.status_code == 400
    assert "已過期" in str(exc.value.detail)


def test_reset_password_should_return_friendly_error_when_token_used(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """重設密碼 token 已使用時應回繁中友善錯誤。"""
    service, repository = auth_service
    user = repository.create_user("user@example.com", hash_password("password123"), "測試者")
    raw_token = "used-token"
    from backend.app.infra.security import hash_password_reset_token

    row = repository.create_password_reset_token(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    row.used_at = datetime.now(timezone.utc)

    with pytest.raises(HTTPException) as exc:
        service.reset_password(raw_token, "new-password-123")
    assert exc.value.status_code == 400
    assert "已使用" in str(exc.value.detail)


def test_reset_password_should_revoke_existing_refresh_tokens(auth_service: tuple[AuthService, FakeAuthRepository]) -> None:
    """重設密碼成功後，既有 refresh token 應全部失效。"""
    service, repository = auth_service
    user = repository.create_user("user@example.com", hash_password("password123"), "測試者")
    login_result = service.login("user@example.com", "password123")
    raw_token = "valid-token"
    from backend.app.infra.security import hash_password_reset_token

    repository.create_password_reset_token(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    message = service.reset_password(raw_token, "new-password-123")
    assert "成功" in message
    reset_token_row = repository.get_password_reset_token_by_hash(hash_password_reset_token(raw_token))
    assert reset_token_row is not None
    assert reset_token_row.used_at is not None

    with pytest.raises(HTTPException):
        service.refresh(login_result.refresh_token)

    with pytest.raises(HTTPException) as reuse_exc:
        service.reset_password(raw_token, "new-password-456")
    assert reuse_exc.value.status_code == 400
    assert "已使用" in str(reuse_exc.value.detail)
