"""健康檢查 API。"""

from fastapi import APIRouter, Depends

from backend.app.domain.schemas.health_schema import HealthResponse
from backend.app.services.health_service import HealthService, get_health_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def get_health(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """回傳服務健康狀態。"""
    return service.get_health_status()
