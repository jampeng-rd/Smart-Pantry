"""Auth 資料存取層。"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.domain.models.refresh_token_model import RefreshToken
from backend.app.domain.models.user_model import User


class AuthRepository:
    """封裝 Auth 相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """依 email 查詢使用者。"""
        statement = select(User).where(User.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def get_user_by_id(self, user_id: int) -> User | None:
        """依 ID 查詢使用者。"""
        statement = select(User).where(User.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def create_user(self, email: str, password_hash: str, display_name: str) -> User:
        """建立新使用者。"""
        user = User(email=email, password_hash=password_hash, display_name=display_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_refresh_token(self, token_hash: str, user_id: int, expires_at: datetime) -> RefreshToken:
        """建立 refresh token 紀錄。"""
        token_row = RefreshToken(token_hash=token_hash, user_id=user_id, expires_at=expires_at)
        self.db.add(token_row)
        self.db.commit()
        self.db.refresh(token_row)
        return token_row

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        """依 hash 查詢 refresh token。"""
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.execute(statement).scalar_one_or_none()

    def revoke_refresh_token(self, token_row: RefreshToken) -> None:
        """撤銷指定 refresh token。"""
        token_row.revoked_at = datetime.now(timezone.utc)
        self.db.add(token_row)
        self.db.commit()

    def revoke_refresh_token_with_replacement(self, token_row: RefreshToken, replacement_id: int) -> None:
        """撤銷舊 token 並設定 replacement token。"""
        token_row.revoked_at = datetime.now(timezone.utc)
        token_row.replaced_by_token_id = replacement_id
        self.db.add(token_row)
        self.db.commit()
