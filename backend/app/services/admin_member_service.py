"""Admin 會員管理商業邏輯服務。"""

from fastapi import HTTPException, status

from backend.app.domain.schemas.admin_member_schema import AdminMemberItem, AdminMemberListResponseData
from backend.app.infra.repository.admin_member_repository import AdminMemberRepository
from backend.app.infra.security import hash_password


class AdminMemberService:
    """處理 Admin 會員查詢與初始化管理員。"""

    def __init__(self, repository: AdminMemberRepository):
        """建立服務實例。"""
        self.repository = repository

    def ensure_admin_user(self, user_id: int) -> None:
        """確認指定使用者具備 admin 權限。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")
        if not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理員權限")

    def list_members(self, page: int, page_size: int) -> AdminMemberListResponseData:
        """查詢會員列表。"""
        rows, total = self.repository.list_members(page=page, page_size=page_size)
        items = [
            AdminMemberItem(
                id=row.id,
                email=row.email,
                display_name=row.display_name,
                is_admin=row.is_admin,
                created_at=row.created_at,
            )
            for row in rows
        ]
        return AdminMemberListResponseData(items=items, page=page, page_size=page_size, total=total)

    def bootstrap_admin(
        self,
        email: str,
        create_if_not_exists: bool = False,
        password: str | None = None,
        display_name: str | None = None,
    ) -> tuple[str, bool]:
        """建立或更新第一個 admin 帳號。"""
        normalized_email = email.strip().lower()
        user = self.repository.get_user_by_email(normalized_email)

        if user is None:
            if not create_if_not_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="找不到指定使用者，請先註冊或使用 --create-if-not-exists。",
                )
            if not password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="建立新 admin 需要提供密碼。")
            final_display_name = (display_name or "系統管理員").strip() or "系統管理員"
            created_user = self.repository.create_user(
                email=normalized_email,
                password_hash=hash_password(password),
                display_name=final_display_name,
                is_admin=True,
            )
            return f"已建立第一個 admin 帳號：{created_user.email}", True

        if user.is_admin:
            return f"使用者已是 admin：{user.email}", False

        user.is_admin = True
        updated_user = self.repository.save_user(user)
        return f"已將使用者設為 admin：{updated_user.email}", True
