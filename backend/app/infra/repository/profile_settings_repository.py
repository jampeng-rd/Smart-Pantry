"""Profile 與 Settings 資料存取層。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.domain.models.user_model import User
from backend.app.domain.models.user_preference_model import UserPreference


class ProfileSettingsRepository:
    """封裝 Profile/Settings 相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        """依 ID 查詢使用者。"""
        statement = select(User).where(User.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def save_user(self, user: User) -> User:
        """儲存使用者資料。"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_preference_by_user_id(self, user_id: int) -> UserPreference | None:
        """依使用者 ID 查詢偏好設定。"""
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def create_preference(
        self,
        user_id: int,
        theme: str = "light-soft",
        timezone_value: str | None = None,
        language: str = "zh-TW",
        expiration_email_reminder_days: str = "1",
    ) -> UserPreference:
        """建立使用者偏好設定。"""
        preference = UserPreference(
            user_id=user_id,
            theme=theme,
            timezone=timezone_value,
            language=language,
            expiration_email_reminder_days=expiration_email_reminder_days,
        )
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference

    def save_preference(self, preference: UserPreference) -> UserPreference:
        """儲存偏好設定。"""
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference
