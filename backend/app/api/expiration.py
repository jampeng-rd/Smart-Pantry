"""Expiration API 路由。"""

from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_current_user_id, get_expiration_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.services.expiration_service import ExpirationService

router = APIRouter(prefix="/expiration", tags=["expiration"])


@router.get("/summary", response_model=ApiResponse)
def get_expiration_summary(
    limit: int = Query(default=10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    service: ExpirationService = Depends(get_expiration_service),
) -> ApiResponse:
    """取得目前登入使用者的過期提醒摘要。"""
    data = service.get_summary(user_id=user_id, items_limit=limit)
    return ApiResponse(status="success", data=data.model_dump(), message=None)
