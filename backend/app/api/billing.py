"""Billing API 路由。"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

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


@router.post("/newebpay/one-time/checkout", response_model=ApiResponse)
def create_newebpay_one_time_checkout(
    user_id: int = Depends(get_current_user_id),
    service: BillingService = Depends(get_billing_service),
) -> ApiResponse:
    """建立藍新單次付款交易並回傳送單資料。"""
    data = service.create_newebpay_one_time_checkout(user_id=user_id)
    return ApiResponse(status="success", data=data.model_dump(mode="json"), message=None)


@router.post("/newebpay/notify")
async def handle_newebpay_notify(
    request: Request,
    service: BillingService = Depends(get_billing_service),
) -> PlainTextResponse:
    """接收藍新背景通知。"""
    form = await request.form()
    payload = dict(form)
    service.handle_newebpay_notify(payload=payload)
    return PlainTextResponse(content="OK")


@router.post("/newebpay/return")
async def handle_newebpay_return(
    request: Request,
    service: BillingService = Depends(get_billing_service),
) -> RedirectResponse:
    """接收藍新前台返回並導向前端結果頁。"""
    form = await request.form()
    payload = dict(form)
    redirect_url = service.build_newebpay_return_redirect_url(payload=payload)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.get("/newebpay/one-time/transactions/{external_trade_no}", response_model=ApiResponse)
def get_newebpay_one_time_transaction_status(
    external_trade_no: str,
    user_id: int = Depends(get_current_user_id),
    service: BillingService = Depends(get_billing_service),
) -> ApiResponse:
    """提供前端結果頁查詢交易狀態。"""
    data = service.get_transaction_status(user_id=user_id, external_trade_no=external_trade_no)
    return ApiResponse(status="success", data=data.model_dump(mode="json"), message=None)
