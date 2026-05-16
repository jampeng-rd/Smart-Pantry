"""Billing API 路由。"""

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_billing_service, get_current_user_id
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/upgrade", response_model=ApiResponse)
def get_billing_upgrade_entry(
    user_id: int = Depends(get_current_user_id),
    service: BillingService = Depends(get_billing_service),
) -> ApiResponse:
    """取得 Billing 升級統一入口設定。"""
    data = service.get_upgrade_entry(user_id=user_id)
    return ApiResponse(status="success", data=data.model_dump(mode="json"), message=None)
