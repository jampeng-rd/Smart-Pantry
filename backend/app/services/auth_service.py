"""Auth 商業邏輯服務。"""

from datetime import datetime

from fastapi import HTTPException, status
from jose import JWTError

from backend.app.domain.schemas.auth_schema import (
    LoginResponseData,
    MeResponseData,
    RefreshResponseData,
    RegisterResponseData,
    UserProfile,
)
from backend.app.infra.repository.auth_repository import AuthRepository
from backend.app.infra.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


class AuthService:
    """處理註冊、登入與 token 流程。"""

    def __init__(self, auth_repository: AuthRepository):
        """建立 Auth 服務實例。"""
        self.auth_repository = auth_repository

    def register(self, email: str, password: str, display_name: str) -> RegisterResponseData:
        """註冊新使用者。"""
        existing_user = self.auth_repository.get_user_by_email(email=email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email 已被註冊")

        user = self.auth_repository.create_user(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
        )
        return RegisterResponseData(user=UserProfile(id=user.id, email=user.email, display_name=user.display_name))

    def login(self, email: str, password: str) -> LoginResponseData:
        """登入並簽發 access/refresh token。"""
        user = self.auth_repository.get_user_by_email(email=email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤")

        access_token, expires_in = create_access_token(user_id=user.id, email=user.email)
        refresh_token, refresh_expires_at = create_refresh_token(user_id=user.id, email=user.email)
        self.auth_repository.create_refresh_token(
            token_hash=hash_refresh_token(refresh_token),
            user_id=user.id,
            expires_at=refresh_expires_at,
        )

        return LoginResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    def refresh(self, refresh_token: str) -> RefreshResponseData:
        """使用 refresh token 取得新的 access/refresh token。"""
        payload = self._decode_refresh_token(refresh_token)

        token_hash = hash_refresh_token(refresh_token)
        token_row = self.auth_repository.get_refresh_token_by_hash(token_hash=token_hash)
        if token_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token 無效")
        if token_row.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token 已失效")
        if token_row.expires_at <= datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token 已過期")

        user = self.auth_repository.get_user_by_id(user_id=token_row.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")

        access_token, expires_in = create_access_token(user_id=user.id, email=user.email)
        new_refresh_token, new_expires_at = create_refresh_token(user_id=user.id, email=user.email)
        new_row = self.auth_repository.create_refresh_token(
            token_hash=hash_refresh_token(new_refresh_token),
            user_id=user.id,
            expires_at=new_expires_at,
        )
        self.auth_repository.revoke_refresh_token_with_replacement(token_row=token_row, replacement_id=new_row.id)

        return RefreshResponseData(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    def logout(self, refresh_token: str) -> None:
        """登出並撤銷 refresh token。"""
        token_hash = hash_refresh_token(refresh_token)
        token_row = self.auth_repository.get_refresh_token_by_hash(token_hash=token_hash)
        if token_row is None:
            return
        if token_row.revoked_at is not None:
            return
        self.auth_repository.revoke_refresh_token(token_row=token_row)

    def get_me(self, access_token: str) -> MeResponseData:
        """取得目前登入使用者資訊。"""
        payload = self._decode_access_token(access_token)
        user_id = int(payload.get("sub", "0"))
        user = self.auth_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")
        return MeResponseData(user=UserProfile(id=user.id, email=user.email, display_name=user.display_name))

    def _decode_refresh_token(self, token: str) -> dict:
        """解碼並驗證 refresh token。"""
        try:
            payload = decode_token(token)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token 無效") from exc
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 類型錯誤")
        return payload

    def _decode_access_token(self, token: str) -> dict:
        """解碼並驗證 access token。"""
        try:
            payload = decode_token(token)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token 無效") from exc
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 類型錯誤")
        return payload
