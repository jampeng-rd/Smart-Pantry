"""Auth API 路由。"""

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_auth_service, get_bearer_token
from backend.app.domain.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse)
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """註冊新使用者。"""
    data = service.register(email=payload.email, password=payload.password, display_name=payload.display_name)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.post("/login", response_model=ApiResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """登入並取得 token。"""
    data = service.login(email=payload.email, password=payload.password)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.post("/refresh", response_model=ApiResponse)
def refresh(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """刷新 access token。"""
    data = service.refresh(refresh_token=payload.refresh_token)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.post("/logout", response_model=ApiResponse)
def logout(payload: LogoutRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """登出並撤銷 refresh token。"""
    service.logout(refresh_token=payload.refresh_token)
    return ApiResponse(status="success", data={"logged_out": True}, message=None)


@router.get("/me", response_model=ApiResponse)
def me(
    access_token: str = Depends(get_bearer_token),
    service: AuthService = Depends(get_auth_service),
) -> ApiResponse:
    """取得當前登入使用者資訊。"""
    data = service.get_me(access_token=access_token)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.post("/forgot-password", response_model=ApiResponse)
def forgot_password(payload: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """送出忘記密碼請求。"""
    message = service.forgot_password(email=payload.email)
    return ApiResponse(status="success", data={"requested": True}, message=message)


@router.post("/reset-password", response_model=ApiResponse)
def reset_password(payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)) -> ApiResponse:
    """使用 token 重設密碼。"""
    message = service.reset_password(token=payload.token, new_password=payload.new_password)
    return ApiResponse(status="success", data={"password_reset": True}, message=message)
