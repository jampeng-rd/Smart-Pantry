"""Recipe recommendation job 相關 Schema。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

JobType = Literal["recipe_recommendation", "receipt_ocr", "ingredient_photo", "nutrition_estimate"]
JobStatus = Literal["pending", "running", "success", "failed", "cancelled"]
RecommendationMode = Literal["selected_items", "auto_from_pantry"]


class RecipeRecommendationJobCreateRequest(BaseModel):
    """建立食譜推薦 job 的請求資料。"""

    recommendation_mode: RecommendationMode
    selected_pantry_item_ids: list[int] | None = None
    prioritize_expiring_soon: bool = False
    cooking_time_minutes: int | None = Field(default=None, ge=1, le=600)
    cooking_tools: list[str] = Field(default_factory=list)
    diet_preference: str | None = None
    allergies: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_selected_items_mode(self) -> "RecipeRecommendationJobCreateRequest":
        """檢查 selected_items 模式的必要欄位。"""
        if self.recommendation_mode == "selected_items" and self.selected_pantry_item_ids is None:
            raise ValueError("selected_items 模式必須提供 selected_pantry_item_ids")
        return self


class RecipeRecommendationJobCreateResponseData(BaseModel):
    """建立食譜推薦 job 回應資料。"""

    job_id: int
    status: JobStatus
    created_at: datetime


class RecipeRecommendationJobStatusResponseData(BaseModel):
    """食譜推薦 job 狀態查詢回應資料。"""

    job_id: int
    status: JobStatus
    result: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
