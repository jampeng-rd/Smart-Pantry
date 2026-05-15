"""Auth 模組 Schema。"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """註冊請求資料。"""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    """登入請求資料。"""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh token 請求資料。"""

    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    """登出請求資料。"""

    refresh_token: str = Field(min_length=1)


class ForgotPasswordRequest(BaseModel):
    """忘記密碼請求資料。"""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """重設密碼請求資料。"""

    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class UserProfile(BaseModel):
    """使用者基本資料。"""

    id: int
    email: EmailStr
    display_name: str
    is_admin: bool


class AuthTokenData(BaseModel):
    """登入或刷新後的 token 回應資料。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponseData(AuthTokenData):
    """登入回應資料。"""


class RegisterResponseData(BaseModel):
    """註冊回應資料。"""

    user: UserProfile


class RefreshResponseData(AuthTokenData):
    """Refresh 回應資料。"""


class MeResponseData(BaseModel):
    """目前登入者回應資料。"""

    user: UserProfile
