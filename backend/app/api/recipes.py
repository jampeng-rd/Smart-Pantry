"""Recipe recommendation jobs API 路由。"""

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_current_user_id, get_recipe_job_service
from backend.app.domain.schemas.common_schema import ApiResponse
from backend.app.domain.schemas.recipe_job_schema import RecipeRecommendationJobCreateRequest
from backend.app.services.recipe_job_service import RecipeJobService

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/recommendation-jobs", response_model=ApiResponse)
def create_recommendation_job(
    payload: RecipeRecommendationJobCreateRequest,
    user_id: int = Depends(get_current_user_id),
    service: RecipeJobService = Depends(get_recipe_job_service),
) -> ApiResponse:
    """建立食譜推薦任務（僅建立 job，不同步等待 AI）。"""
    data = service.create_recommendation_job(user_id=user_id, payload=payload)
    return ApiResponse(status="success", data=data.model_dump(), message=None)


@router.get("/recommendation-jobs/{job_id}", response_model=ApiResponse)
def get_recommendation_job_status(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    service: RecipeJobService = Depends(get_recipe_job_service),
) -> ApiResponse:
    """查詢食譜推薦任務狀態（僅限查詢自己的 job）。"""
    data = service.get_recommendation_job_status(user_id=user_id, job_id=job_id)
    return ApiResponse(status="success", data=data.model_dump(), message=None)
