"""Recipe recommendation job 商業邏輯服務。"""

from datetime import date, timedelta

from fastapi import HTTPException, status

from backend.app.domain.schemas.recipe_job_schema import (
    RecipeRecommendationJobCreateRequest,
    RecipeRecommendationJobCreateResponseData,
    RecipeRecommendationJobStatusResponseData,
)
from backend.app.infra.repository.ai_job_repository import AiJobRepository


class RecipeJobService:
    """處理 recipe recommendation job 的建立與查詢。"""

    def __init__(self, ai_job_repository: AiJobRepository):
        """建立 RecipeJobService 實例。"""
        self.ai_job_repository = ai_job_repository

    def create_recommendation_job(self, user_id: int, payload: RecipeRecommendationJobCreateRequest) -> RecipeRecommendationJobCreateResponseData:
        """建立 recipe recommendation job。"""
        input_snapshot = self._build_input_snapshot(user_id=user_id, payload=payload)
        job = self.ai_job_repository.create_job(
            user_id=user_id,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot=input_snapshot,
        )
        return RecipeRecommendationJobCreateResponseData(job_id=job.id, status=job.status, created_at=job.created_at)

    def get_recommendation_job_status(self, user_id: int, job_id: int) -> RecipeRecommendationJobStatusResponseData:
        """取得目前登入使用者的 recipe recommendation job 狀態。"""
        job = self.ai_job_repository.get_job_by_id_and_user_id(job_id=job_id, user_id=user_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到對應的 AI 任務")

        safe_error_message = job.error_message
        if job.status == "failed" and not safe_error_message:
            safe_error_message = "任務處理失敗，請稍後再試。"

        return RecipeRecommendationJobStatusResponseData(
            job_id=job.id,
            status=job.status,
            result=job.result,
            error_message=safe_error_message,
            created_at=job.created_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
        )

    def _build_input_snapshot(self, user_id: int, payload: RecipeRecommendationJobCreateRequest) -> dict:
        """建立可追蹤的 input snapshot。"""
        selected_ids = payload.selected_pantry_item_ids or []

        if payload.recommendation_mode == "selected_items":
            if not selected_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="selected_items 模式至少需選擇一筆食材")

            unique_ids = sorted(set(selected_ids))
            pantry_items = self.ai_job_repository.list_pantry_items_by_ids_and_user_id(item_ids=unique_ids, user_id=user_id)
            if len(pantry_items) != len(unique_ids):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所選食材不存在或不屬於目前使用者")

            resolved_pantry_items = [self._to_pantry_snapshot(item) for item in pantry_items]
        else:
            resolved_pantry_items = []

        return {
            "recommendation_mode": payload.recommendation_mode,
            "selected_pantry_item_ids": selected_ids,
            "resolved_pantry_items": resolved_pantry_items,
            "pending_auto_selection": payload.recommendation_mode == "auto_from_pantry",
            "prioritize_expiring_soon": payload.prioritize_expiring_soon,
            "cooking_time_minutes": payload.cooking_time_minutes,
            "cooking_tools": payload.cooking_tools,
            "diet_preference": payload.diet_preference,
            "allergies": payload.allergies,
        }

    def _to_pantry_snapshot(self, pantry_item) -> dict:
        """將 pantry item 轉為 input_snapshot 可用摘要。"""
        return {
            "id": pantry_item.id,
            "name": pantry_item.name,
            "category": pantry_item.category,
            "quantity": float(pantry_item.quantity),
            "unit": pantry_item.unit,
            "expiration_date": pantry_item.expiration_date.isoformat() if pantry_item.expiration_date else None,
            "status": self._get_pantry_status(pantry_item.expiration_date),
        }

    def _get_pantry_status(self, expiration_date: date | None) -> str:
        """依 expiration_date 計算食材狀態字串。"""
        if expiration_date is None:
            return "normal"

        today = date.today()
        soon_end = today + timedelta(days=3)
        if expiration_date < today:
            return "expired"
        if today <= expiration_date <= soon_end:
            return "expiring_soon"
        return "normal"
