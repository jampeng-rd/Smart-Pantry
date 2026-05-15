"""Admin 會員管理 API 路由。"""

from fastapi import APIRouter, Depends, Query

from backend.app.admin_api.dependencies import get_admin_member_service, get_current_admin_user_id
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.services.admin_member_service import AdminMemberService

router = APIRouter(prefix="/admin/members", tags=["admin-members"])


@router.get("", response_model=ApiResponse)
def list_members(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: int = Depends(get_current_admin_user_id),
    service: AdminMemberService = Depends(get_admin_member_service),
) -> ApiResponse:
    """查詢會員列表（僅 admin 可用）。"""
    data = service.list_members(page=page, page_size=page_size)
    return ApiResponse(status="success", data=data.model_dump(), message=None)
