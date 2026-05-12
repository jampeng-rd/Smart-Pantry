"""Profile API 路由。"""

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_current_user_id, get_profile_settings_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.domain.schemas.profile_settings_schema import ChangePasswordRequest, ProfileUpdateRequest
from backend.app.services.profile_settings_service import ProfileSettingsService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ApiResponse)
def get_profile(
    user_id: int = Depends(get_current_user_id),
    service: ProfileSettingsService = Depends(get_profile_settings_service),
) -> ApiResponse:
    """取得目前登入使用者個人資料。"""
    data = service.get_profile(user_id=user_id)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.patch("", response_model=ApiResponse)
def patch_profile(
    payload: ProfileUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    service: ProfileSettingsService = Depends(get_profile_settings_service),
) -> ApiResponse:
    """更新目前登入使用者名稱。"""
    data = service.update_profile(user_id=user_id, display_name=payload.display_name)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.post("/change-password", response_model=ApiResponse)
def change_password(
    payload: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    service: ProfileSettingsService = Depends(get_profile_settings_service),
) -> ApiResponse:
    """修改目前登入使用者密碼。"""
    service.change_password(user_id=user_id, current_password=payload.current_password, new_password=payload.new_password)
    return ApiResponse(status="success", data={"password_changed": True}, message=None)
