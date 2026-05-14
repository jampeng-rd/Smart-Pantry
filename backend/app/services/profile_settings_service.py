"""Profile 與 Settings 商業邏輯服務。"""

from fastapi import HTTPException, status

from backend.app.domain.schemas.profile_settings_schema import (
    ExpirationReminderDeliveryItem,
    ExpirationReminderDeliveryListResponseData,
    ProfileResponseData,
    SettingsResponseData,
)
from backend.app.infra.repository.profile_settings_repository import ProfileSettingsRepository
from backend.app.infra.security import hash_password, verify_password


class ProfileSettingsService:
    """處理個人資料與偏好設定。"""

    def __init__(self, repository: ProfileSettingsRepository):
        """建立服務實例。"""
        self.repository = repository

    def get_profile(self, user_id: int) -> ProfileResponseData:
        """取得目前登入使用者個人資料。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        fallback = (user.display_name or "?").strip()[:1] or "?"
        return ProfileResponseData(
            display_name=user.display_name,
            email=user.email,
            avatar_url=None,
            avatar_fallback=fallback,
        )

    def update_profile(self, user_id: int, display_name: str) -> ProfileResponseData:
        """更新目前登入使用者顯示名稱。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        user.display_name = display_name.strip()
        updated_user = self.repository.save_user(user)

        fallback = (updated_user.display_name or "?").strip()[:1] or "?"
        return ProfileResponseData(
            display_name=updated_user.display_name,
            email=updated_user.email,
            avatar_url=None,
            avatar_fallback=fallback,
        )

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """修改目前登入使用者密碼。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目前密碼錯誤")

        user.password_hash = hash_password(new_password)
        self.repository.save_user(user)

    def get_settings(self, user_id: int) -> SettingsResponseData:
        """取得目前登入使用者設定。"""
        self._ensure_user_exists(user_id=user_id)
        preference = self._get_or_create_preference(user_id=user_id)
        return self._to_settings_response(preference)

    def update_settings(
        self,
        user_id: int,
        theme: str | None,
        timezone_value: str | None,
        expiration_email_reminder_days: str | None,
    ) -> SettingsResponseData:
        """更新目前登入使用者設定。"""
        self._ensure_user_exists(user_id=user_id)
        preference = self._get_or_create_preference(user_id=user_id)

        if theme is not None:
            preference.theme = theme
        if timezone_value is not None:
            preference.timezone = timezone_value.strip() or None
        if expiration_email_reminder_days is not None:
            preference.expiration_email_reminder_days = expiration_email_reminder_days

        updated_preference = self.repository.save_preference(preference)
        return self._to_settings_response(updated_preference)

    def list_expiration_reminder_deliveries(self, user_id: int, page: int, page_size: int) -> ExpirationReminderDeliveryListResponseData:
        """查詢目前登入使用者到期提醒寄送紀錄。"""
        self._ensure_user_exists(user_id=user_id)
        rows, total = self.repository.list_expiration_reminder_deliveries(user_id=user_id, page=page, page_size=page_size)

        items = [
            ExpirationReminderDeliveryItem(
                id=row.id,
                scheduled_date=row.scheduled_date,
                send_window=row.send_window,
                reminder_days=row.reminder_days,
                item_ids=row.item_ids,
                item_count=len(row.item_ids),
                email_to=row.email_to,
                status=row.status,
                final_status=row.final_status,
                attempt_count=row.attempt_count,
                last_error_message=row.last_error_message,
                last_attempt_at=row.last_attempt_at,
                sent_at=row.sent_at,
                error_message=row.error_message,
                created_at=row.created_at,
            )
            for row in rows
        ]
        return ExpirationReminderDeliveryListResponseData(items=items, page=page, page_size=page_size, total=total)

    def _ensure_user_exists(self, user_id: int) -> None:
        """確認使用者存在。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

    def _get_or_create_preference(self, user_id: int):
        """取得偏好設定，若不存在則建立預設值。"""
        preference = self.repository.get_preference_by_user_id(user_id=user_id)
        if preference is None:
            preference = self.repository.create_preference(user_id=user_id)
        return preference

    def _to_settings_response(self, preference) -> SettingsResponseData:
        """轉換成設定回應資料。"""
        return SettingsResponseData(
            theme=preference.theme,
            timezone=preference.timezone,
            language=preference.language,
            expiration_email_reminder_days=preference.expiration_email_reminder_days,
        )
