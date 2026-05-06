"""健康檢查服務。"""

from backend.app.domain.schemas.health_schema import HealthResponse


class HealthService:
    """提供健康檢查回應的服務類別。"""

    def get_health_status(self) -> HealthResponse:
        """取得目前 API 可用狀態。"""
        return HealthResponse(status="ok", service="smartpantry-backend")


def get_health_service() -> HealthService:
    """提供健康檢查服務依賴。"""
    return HealthService()
