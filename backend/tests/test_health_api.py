"""健康檢查 API 測試。"""

from backend.app.api.health import get_health
from backend.app.services.health_service import HealthService


def test_health_api_should_return_ok_status() -> None:
    """驗證健康檢查 API 可回傳成功狀態。"""
    response = get_health(service=HealthService())
    assert response.model_dump() == {"status": "ok", "service": "smartpantry-backend"}
