"""Ingredient photo job 相關 Schema。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from backend.app.domain.schemas.recipe_job_schema import JobStatus


class IngredientPhotoJobCreateResponseData(BaseModel):
    """建立食材照片辨識 job 回應資料。"""

    job_id: int
    status: JobStatus
    created_at: datetime


class IngredientPhotoJobStatusResponseData(BaseModel):
    """食材照片辨識 job 狀態查詢回應資料。"""

    job_id: int
    status: JobStatus
    result: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
