"""Admin API 依賴注入工具。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user_id
from backend.app.infra.database import get_db_session
from backend.app.infra.repository.admin_member_repository import AdminMemberRepository
from backend.app.services.admin_member_service import AdminMemberService


def get_admin_member_service(db: Session = Depends(get_db_session)) -> AdminMemberService:
    """提供 AdminMemberService 依賴。"""
    repository = AdminMemberRepository(db=db)
    return AdminMemberService(repository=repository)


def get_current_admin_user_id(
    user_id: int = Depends(get_current_user_id),
    service: AdminMemberService = Depends(get_admin_member_service),
) -> int:
    """取得目前 admin 使用者 ID，非 admin 直接拒絕。"""
    service.ensure_admin_user(user_id=user_id)
    return user_id
