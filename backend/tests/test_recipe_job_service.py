"""Recipe recommendation job 服務測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from backend.app.domain.schemas.recipe_job_schema import RecipeRecommendationJobCreateRequest
from backend.app.services.recipe_job_service import RecipeJobService


@dataclass
class FakePantryItem:
    """測試用 pantry item。"""

    id: int
    user_id: int
    name: str
    category: str
    quantity: Decimal
    unit: str
    expiration_date: date | None


@dataclass
class FakeAiJob:
    """測試用 ai job。"""

    id: int
    user_id: int
    job_type: str
    status: str
    input_snapshot: dict
    result: dict | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class FakeAiJobRepository:
    """以記憶體模擬 AiJobRepository。"""

    def __init__(self) -> None:
        """初始化假資料儲存。"""
        self.pantry_items: dict[int, FakePantryItem] = {}
        self.jobs: dict[int, FakeAiJob] = {}
        self._seq = 1

    def seed_pantry_item(self, item: FakePantryItem) -> None:
        """加入測試 pantry item。"""
        self.pantry_items[item.id] = item

    def create_job(self, user_id: int, job_type: str, status: str, input_snapshot: dict) -> FakeAiJob:
        """建立測試 job。"""
        job = FakeAiJob(
            id=self._seq,
            user_id=user_id,
            job_type=job_type,
            status=status,
            input_snapshot=input_snapshot,
            result=None,
            error_message=None,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            finished_at=None,
        )
        self.jobs[job.id] = job
        self._seq += 1
        return job

    def get_job_by_id_and_user_id(self, job_id: int, user_id: int) -> FakeAiJob | None:
        """依 job_id 與 user_id 查詢 job。"""
        job = self.jobs.get(job_id)
        if job is None or job.user_id != user_id:
            return None
        return job

    def list_pantry_items_by_ids_and_user_id(self, item_ids: list[int], user_id: int) -> list[FakePantryItem]:
        """查詢屬於使用者的 pantry items。"""
        rows = [self.pantry_items[item_id] for item_id in item_ids if item_id in self.pantry_items]
        return [item for item in rows if item.user_id == user_id]


@pytest.fixture
def recipe_job_service() -> tuple[RecipeJobService, FakeAiJobRepository]:
    """建立 RecipeJobService 與假 repository。"""
    repository = FakeAiJobRepository()
    return RecipeJobService(ai_job_repository=repository), repository


def test_selected_items_mode_can_create_pending_job(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """selected_items 模式可建立 pending job。"""
    service, repository = recipe_job_service
    repository.seed_pantry_item(
        FakePantryItem(id=1, user_id=101, name="雞蛋", category="蛋類", quantity=Decimal("3"), unit="顆", expiration_date=None)
    )

    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="selected_items", selected_pantry_item_ids=[1])
    result = service.create_recommendation_job(user_id=101, payload=payload)

    assert result.status == "pending"
    assert result.job_id == 1


def test_selected_items_mode_requires_owned_items(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """selected_items 模式必須驗證 item 屬於目前使用者。"""
    service, repository = recipe_job_service
    repository.seed_pantry_item(
        FakePantryItem(id=7, user_id=202, name="牛奶", category="乳品", quantity=Decimal("1"), unit="瓶", expiration_date=None)
    )
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="selected_items", selected_pantry_item_ids=[7])

    with pytest.raises(HTTPException) as exc:
        service.create_recommendation_job(user_id=101, payload=payload)

    assert exc.value.status_code == 400
    assert "不屬於目前使用者" in str(exc.value.detail)


def test_selected_items_mode_rejects_empty_list(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """selected_items 空陣列應回傳可理解錯誤。"""
    service, _ = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="selected_items", selected_pantry_item_ids=[])

    with pytest.raises(HTTPException) as exc:
        service.create_recommendation_job(user_id=101, payload=payload)

    assert exc.value.status_code == 400
    assert "至少需選擇一筆食材" in str(exc.value.detail)


def test_auto_from_pantry_mode_can_create_pending_job(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """auto_from_pantry 模式本階段可建立 pending job。"""
    service, _ = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry", prioritize_expiring_soon=True)

    result = service.create_recommendation_job(user_id=101, payload=payload)

    assert result.status == "pending"
    status_payload = service.get_recommendation_job_status(user_id=101, job_id=result.job_id)
    assert status_payload.result is None


def test_input_snapshot_records_recommendation_mode(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """input_snapshot 應記錄 recommendation_mode。"""
    service, repository = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry")

    result = service.create_recommendation_job(user_id=101, payload=payload)
    job = repository.jobs[result.job_id]

    assert job.input_snapshot["recommendation_mode"] == "auto_from_pantry"
    assert job.input_snapshot["pending_auto_selection"] is True


def test_get_own_job_status_success(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """可查詢自己的 job 狀態。"""
    service, repository = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry")
    created = service.create_recommendation_job(user_id=101, payload=payload)

    repository.jobs[created.job_id].status = "success"
    repository.jobs[created.job_id].result = {"recipes": [{"name": "測試食譜"}]}

    status_payload = service.get_recommendation_job_status(user_id=101, job_id=created.job_id)

    assert status_payload.status == "success"
    assert status_payload.result == {"recipes": [{"name": "測試食譜"}]}


def test_cannot_read_other_user_job(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """不可查詢其他使用者 job。"""
    service, _ = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry")
    created = service.create_recommendation_job(user_id=101, payload=payload)

    with pytest.raises(HTTPException) as exc:
        service.get_recommendation_job_status(user_id=202, job_id=created.job_id)

    assert exc.value.status_code == 404


def test_job_status_response_shape(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """job status 回應欄位格式應完整。"""
    service, repository = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry")
    created = service.create_recommendation_job(user_id=101, payload=payload)
    repository.jobs[created.job_id].status = "failed"
    repository.jobs[created.job_id].error_message = "暫時無法完成任務"

    status_payload = service.get_recommendation_job_status(user_id=101, job_id=created.job_id).model_dump()

    assert set(status_payload.keys()) == {
        "job_id",
        "status",
        "result",
        "error_message",
        "created_at",
        "started_at",
        "finished_at",
    }
    assert status_payload["status"] == "failed"


def test_service_does_not_call_real_ollama(recipe_job_service: tuple[RecipeJobService, FakeAiJobRepository]) -> None:
    """本階段不呼叫任何真實 Ollama。"""
    service, _ = recipe_job_service
    payload = RecipeRecommendationJobCreateRequest(recommendation_mode="auto_from_pantry")

    result = service.create_recommendation_job(user_id=101, payload=payload)

    assert result.status == "pending"
