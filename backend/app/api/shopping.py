"""Shopping API 路由。"""

from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_current_user_id, get_shopping_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.domain.schemas.shopping_schema import ShoppingItemCreateRequest, ShoppingItemUpdateRequest, ShoppingSortType
from backend.app.services.shopping_service import ShoppingService

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.post("/items", response_model=ApiResponse)
def create_shopping_item(
    payload: ShoppingItemCreateRequest,
    user_id: int = Depends(get_current_user_id),
    service: ShoppingService = Depends(get_shopping_service),
) -> ApiResponse:
    """新增目前登入使用者購物清單項目。"""
    data = service.create_item(
        user_id=user_id,
        source_pantry_item_id=payload.source_pantry_item_id,
        name=payload.name,
        quantity=payload.quantity,
        unit=payload.unit,
    )
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.get("/items", response_model=ApiResponse)
def list_shopping_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_purchased: bool | None = Query(default=None),
    q: str | None = Query(default=None),
    sort: ShoppingSortType = Query(default="created_at"),
    user_id: int = Depends(get_current_user_id),
    service: ShoppingService = Depends(get_shopping_service),
) -> ApiResponse:
    """查詢目前登入使用者購物清單。"""
    data = service.list_items(
        user_id=user_id,
        page=page,
        page_size=page_size,
        is_purchased=is_purchased,
        q=q,
        sort=sort,
    )
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.patch("/items/{item_id}", response_model=ApiResponse)
def update_shopping_item(
    item_id: int,
    payload: ShoppingItemUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    service: ShoppingService = Depends(get_shopping_service),
) -> ApiResponse:
    """更新目前登入使用者購物清單項目。"""
    data = service.update_item(user_id=user_id, item_id=item_id, update_fields=payload.model_dump())
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.delete("/items/{item_id}", response_model=ApiResponse)
def delete_shopping_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ShoppingService = Depends(get_shopping_service),
) -> ApiResponse:
    """刪除目前登入使用者購物清單項目。"""
    service.delete_item(user_id=user_id, item_id=item_id)
    return ApiResponse(status="success", data={"deleted": True}, message=None)
