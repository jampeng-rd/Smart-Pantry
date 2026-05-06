"""共用 API 回應 Schema。"""

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """統一 API 回應格式。"""

    status: str
    data: Any | None
    message: str | None
