"""Settings API 路由。"""

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_current_user_id, get_profile_settings_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.domain.schemas.profile_settings_schema import SettingsUpdateRequest
from backend.app.services.profile_settings_service import ProfileSettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=ApiResponse)
def get_settings(
    user_id: int = Depends(get_current_user_id),
    service: ProfileSettingsService = Depends(get_profile_settings_service),
) -> ApiResponse:
    """取得目前登入使用者設定。"""
    data = service.get_settings(user_id=user_id)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.patch("", response_model=ApiResponse)
def patch_settings(
    payload: SettingsUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    service: ProfileSettingsService = Depends(get_profile_settings_service),
) -> ApiResponse:
    """更新目前登入使用者設定。"""
    data = service.update_settings(
        user_id=user_id,
        theme=payload.theme,
        timezone_value=payload.timezone,
        expiration_email_reminder_days=payload.expiration_email_reminder_days,
    )
    return ApiResponse(status="success", data=data.model_dump(), message=None)
