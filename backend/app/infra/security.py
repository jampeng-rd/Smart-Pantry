"""安全相關工具：密碼與 JWT。"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.infra.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    """將使用者密碼雜湊。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼與雜湊值是否一致。"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, email: str) -> tuple[str, int]:
    """建立 access token，並回傳 token 與秒數。"""
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: int, email: str) -> tuple[str, datetime]:
    """建立 refresh token，並回傳 token 與過期時間。"""
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "jti": secrets.token_hex(16),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def hash_refresh_token(refresh_token: str) -> str:
    """將 refresh token 轉為 SHA-256 hash。"""
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def create_password_reset_token() -> str:
    """建立重設密碼用的一次性明文 token。"""
    return secrets.token_urlsafe(32)


def hash_password_reset_token(reset_token: str) -> str:
    """將重設密碼 token 轉為 SHA-256 hash。"""
    return hashlib.sha256(reset_token.encode("utf-8")).hexdigest()


def decode_token(token: str) -> dict:
    """解碼 JWT token。"""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def is_token_expired(token: str) -> bool:
    """檢查 token 是否已過期或無效。"""
    try:
        decode_token(token)
        return False
    except JWTError:
        return True
