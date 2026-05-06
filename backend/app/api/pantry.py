"""Pantry API 路由。"""

from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_current_user_id, get_pantry_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.domain.schemas.pantry_schema import PantryItemCreateRequest, PantryItemUpdateRequest
from backend.app.services.pantry_service import PantryService

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.post("/items", response_model=ApiResponse)
def create_pantry_item(
    payload: PantryItemCreateRequest,
    user_id: int = Depends(get_current_user_id),
    service: PantryService = Depends(get_pantry_service),
) -> ApiResponse:
    """新增目前登入使用者食材。"""
    data = service.create_item(
        user_id=user_id,
        name=payload.name,
        category=payload.category,
        quantity=payload.quantity,
        unit=payload.unit,
        expiration_date=payload.expiration_date,
        storage_location=payload.storage_location,
        note=payload.note,
    )
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.get("/items", response_model=ApiResponse)
def list_pantry_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    user_id: int = Depends(get_current_user_id),
    service: PantryService = Depends(get_pantry_service),
) -> ApiResponse:
    """查詢目前登入使用者食材列表。"""
    data = service.list_items(
        user_id=user_id,
        page=page,
        page_size=page_size,
        category=category,
        q=q,
        sort=sort,
    )
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.patch("/items/{item_id}", response_model=ApiResponse)
def update_pantry_item(
    item_id: int,
    payload: PantryItemUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    service: PantryService = Depends(get_pantry_service),
) -> ApiResponse:
    """更新目前登入使用者食材。"""
    data = service.update_item(user_id=user_id, item_id=item_id, update_fields=payload.model_dump())
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.delete("/items/{item_id}", response_model=ApiResponse)
def delete_pantry_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    service: PantryService = Depends(get_pantry_service),
) -> ApiResponse:
    """刪除目前登入使用者食材。"""
    service.delete_item(user_id=user_id, item_id=item_id)
    return ApiResponse(status="success", data={"deleted": True}, message=None)
