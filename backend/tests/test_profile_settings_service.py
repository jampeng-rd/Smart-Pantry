"""Profile 與 Settings 服務單元測試。"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.domain.schemas.profile_settings_schema import SettingsUpdateRequest
from backend.app.infra.security import hash_password, verify_password
from backend.app.services.profile_settings_service import ProfileSettingsService


@dataclass
class FakeUser:
    """測試用使用者資料。"""

    id: int
    email: str
    display_name: str
    password_hash: str


@dataclass
class FakePreference:
    """測試用偏好設定資料。"""

    id: int
    user_id: int
    theme: str
    timezone: str | None
    language: str
    expiration_email_reminder_days: str


class FakeProfileSettingsRepository:
    """以記憶體模擬 ProfileSettingsRepository。"""

    def __init__(self) -> None:
        """初始化假資料。"""
        self.users: dict[int, FakeUser] = {
            1: FakeUser(id=1, email="a@example.com", display_name="小明", password_hash=hash_password("old-password")),
            2: FakeUser(id=2, email="b@example.com", display_name="Bob", password_hash=hash_password("password-2")),
        }
        self.preferences: dict[int, FakePreference] = {}
        self._pref_seq = 1

    def get_user_by_id(self, user_id: int) -> FakeUser | None:
        """依 ID 查詢使用者。"""
        return self.users.get(user_id)

    def save_user(self, user: FakeUser) -> FakeUser:
        """儲存使用者。"""
        self.users[user.id] = user
        return user

    def get_preference_by_user_id(self, user_id: int) -> FakePreference | None:
        """依 user_id 查詢偏好。"""
        return self.preferences.get(user_id)

    def create_preference(
        self,
        user_id: int,
        theme: str = "light-soft",
        timezone_value: str | None = None,
        language: str = "zh-TW",
        expiration_email_reminder_days: str = "1",
    ) -> FakePreference:
        """建立偏好設定。"""
        pref = FakePreference(
            id=self._pref_seq,
            user_id=user_id,
            theme=theme,
            timezone=timezone_value,
            language=language,
            expiration_email_reminder_days=expiration_email_reminder_days,
        )
        self.preferences[user_id] = pref
        self._pref_seq += 1
        return pref

    def save_preference(self, preference: FakePreference) -> FakePreference:
        """儲存偏好設定。"""
        self.preferences[preference.user_id] = preference
        return preference


@pytest.fixture
def profile_settings_service() -> tuple[ProfileSettingsService, FakeProfileSettingsRepository]:
    """建立 ProfileSettingsService 與假 repository。"""
    repository = FakeProfileSettingsRepository()
    return ProfileSettingsService(repository=repository), repository


def test_get_profile_success(profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository]) -> None:
    """GET /profile 應可取得個人資料。"""
    service, _ = profile_settings_service

    result = service.get_profile(user_id=1)

    assert result.display_name == "小明"
    assert result.email == "a@example.com"
    assert result.avatar_url is None
    assert result.avatar_fallback == "小"


def test_patch_profile_update_display_name(profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository]) -> None:
    """PATCH /profile 應可更新 display_name。"""
    service, repository = profile_settings_service

    result = service.update_profile(user_id=1, display_name="小華")

    assert result.display_name == "小華"
    assert repository.users[1].display_name == "小華"


def test_email_cannot_be_modified(profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository]) -> None:
    """更新個人資料不應修改 email。"""
    service, repository = profile_settings_service

    service.update_profile(user_id=1, display_name="小新")

    assert repository.users[1].email == "a@example.com"


def test_change_password_should_fail_when_current_password_wrong(
    profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository],
) -> None:
    """目前密碼錯誤時應失敗。"""
    service, _ = profile_settings_service

    with pytest.raises(HTTPException) as exc:
        service.change_password(user_id=1, current_password="wrong-password", new_password="new-password-123")

    assert exc.value.status_code == 400


def test_change_password_success_should_update_hash(
    profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository],
) -> None:
    """修改密碼成功後，password hash 應更新且可驗證新密碼。"""
    service, repository = profile_settings_service

    old_hash = repository.users[1].password_hash
    service.change_password(user_id=1, current_password="old-password", new_password="new-password-123")
    new_hash = repository.users[1].password_hash

    assert old_hash != new_hash
    assert verify_password("new-password-123", new_hash)


def test_get_settings_should_create_defaults_when_missing(
    profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository],
) -> None:
    """GET /settings 在偏好不存在時應建立預設值。"""
    service, repository = profile_settings_service

    result = service.get_settings(user_id=1)

    assert result.theme == "light-soft"
    assert result.language == "zh-TW"
    assert result.expiration_email_reminder_days == "1"
    assert repository.preferences[1].expiration_email_reminder_days == "1"


def test_patch_settings_should_update_allowed_fields(
    profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository],
) -> None:
    """PATCH /settings 應可更新 theme/timezone/reminder。"""
    service, _ = profile_settings_service

    result = service.update_settings(
        user_id=1,
        theme="dark-soft",
        timezone_value="Asia/Taipei",
        expiration_email_reminder_days="3",
    )

    assert result.theme == "dark-soft"
    assert result.timezone == "Asia/Taipei"
    assert result.expiration_email_reminder_days == "3"


def test_get_settings_should_not_cross_user(
    profile_settings_service: tuple[ProfileSettingsService, FakeProfileSettingsRepository],
) -> None:
    """不可跨使用者讀取設定。"""
    service, _ = profile_settings_service

    service.update_settings(user_id=1, theme="dark-soft", timezone_value="Asia/Taipei", expiration_email_reminder_days="3")
    other_user = service.get_settings(user_id=2)

    assert other_user.theme == "light-soft"
    assert other_user.expiration_email_reminder_days == "1"


def test_expiration_email_reminder_days_should_reject_invalid_value() -> None:
    """expiration_email_reminder_days 僅允許 none/1/3。"""
    with pytest.raises(ValidationError):
        SettingsUpdateRequest(expiration_email_reminder_days="7")
