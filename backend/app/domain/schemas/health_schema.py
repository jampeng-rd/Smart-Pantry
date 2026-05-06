"""健康檢查 Schema。"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """健康檢查 API 回應格式。"""

    status: str = Field(description="服務狀態")
    service: str = Field(description="服務名稱")
