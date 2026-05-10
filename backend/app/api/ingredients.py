"""Ingredient photo jobs API 路由。"""

from fastapi import APIRouter, Depends, File, UploadFile

from backend.app.api.dependencies import get_current_user_id, get_ingredient_photo_job_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.services.ingredient_photo_job_service import IngredientPhotoJobService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("/photo/jobs", response_model=ApiResponse)
def create_photo_job(
    image: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    service: IngredientPhotoJobService = Depends(get_ingredient_photo_job_service),
) -> ApiResponse:
    """建立食材照片辨識任務（僅建立 job，不同步等待 AI）。"""
    data = service.create_photo_job(user_id=user_id, image=image)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.get("/photo/jobs/{job_id}", response_model=ApiResponse)
def get_photo_job_status(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    service: IngredientPhotoJobService = Depends(get_ingredient_photo_job_service),
) -> ApiResponse:
    """查詢食材照片辨識任務狀態（僅限查詢自己的 job）。"""
    data = service.get_photo_job_status(user_id=user_id, job_id=job_id)
    return ApiResponse(status="success", data=data.model_dump(), message=None)
