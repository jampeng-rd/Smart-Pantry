"""Admin 會員管理資料存取層。"""

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from backend.app.domain.models.user_model import User


class AdminMemberRepository:
    """封裝 Admin 會員管理相關資料庫操作。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        """依使用者 ID 查詢使用者。"""
        statement = select(User).where(User.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_user_by_email(self, email: str) -> User | None:
        """依 Email 查詢使用者。"""
        statement = select(User).where(User.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def create_user(self, email: str, password_hash: str, display_name: str, is_admin: bool) -> User:
        """建立新使用者。"""
        user = User(email=email, password_hash=password_hash, display_name=display_name, is_admin=is_admin)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save_user(self, user: User) -> User:
        """儲存使用者變更。"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_members(self, page: int, page_size: int) -> tuple[list[User], int]:
        """分頁查詢會員列表（最新建立優先）。"""
        total_statement = select(func.count(User.id))
        total = self.db.execute(total_statement).scalar_one()

        statement = (
            select(User)
            .order_by(desc(User.created_at), desc(User.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = list(self.db.execute(statement).scalars().all())
        return rows, total
