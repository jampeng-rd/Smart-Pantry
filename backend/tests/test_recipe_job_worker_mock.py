"""Phase 08-1 recipe mock worker 單元測試。"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ai_server.workers.job_worker import _claim_pending_jobs, _process_ingredient_photo_job, _process_recipe_job
from ai_server.app.services.recipe_recommendation_service import RecipeRecommendationService
from backend.app.domain.models import AiJob, Base, PantryItem, User


class FakeRecipeLlmClient:
    """測試用假 LLM client。"""

    def __init__(self, response_text: str):
        """設定固定回傳內容。"""
        self.response_text = response_text

    def generate_recipe_json(self, prompt: str) -> str:
        """回傳預設字串。"""
        _ = prompt
        return self.response_text


def _make_recipe_service(response_text: str) -> RecipeRecommendationService:
    """建立可注入固定回傳的 recipe service。"""
    return RecipeRecommendationService(llm_client=FakeRecipeLlmClient(response_text=response_text))


def _make_session() -> Session:
    """建立測試用 in-memory DB session。"""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)()


def _create_user(db: Session, user_id: int, email: str) -> None:
    """建立測試使用者。"""
    db.add(User(id=user_id, email=email, password_hash="hashed", display_name=f"user-{user_id}"))
    db.commit()


def test_selected_items_job_processed_to_success() -> None:
    """selected_items 模式可由 mock worker 處理為 success。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={
                "recommendation_mode": "selected_items",
                "resolved_pantry_items": [
                    {"id": 10, "name": "雞蛋", "category": "蛋類", "quantity": 2, "unit": "顆", "status": "normal"}
                ],
                "cooking_time_minutes": 15,
            },
        )
    )
    db.commit()

    jobs = _claim_pending_jobs(db=db, batch_size=5, enabled_job_types=["recipe_recommendation"])
    assert len(jobs) == 1
    recipe_service = _make_recipe_service(
        '{"recipe_name":"雞蛋豆腐","ingredients_used":["雞蛋"],"missing_ingredients":["鹽"],"steps":["攪拌","拌炒"],"cooking_time_minutes":15,"note":"僅供生活參考"}'
    )
    _process_recipe_job(db=db, job=jobs[0], recipe_service=recipe_service)

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "success"
    assert job.result is not None
    assert job.result["recipe_name"]
    assert set(job.result.keys()) == {
        "recipe_name",
        "ingredients_used",
        "missing_ingredients",
        "steps",
        "cooking_time_minutes",
        "note",
    }


def test_auto_from_pantry_job_processed_to_success() -> None:
    """auto_from_pantry 模式可由 mock worker 處理為 success。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        PantryItem(
            user_id=1,
            name="豆腐",
            category="豆製品",
            quantity=1,
            unit="盒",
            expiration_date=date.today() + timedelta(days=1),
            storage_location="fridge",
            note=None,
        )
    )
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={"recommendation_mode": "auto_from_pantry", "cooking_time_minutes": 25},
        )
    )
    db.commit()

    jobs = _claim_pending_jobs(db=db, batch_size=5, enabled_job_types=["recipe_recommendation"])
    recipe_service = _make_recipe_service(
        '{"recipe_name":"豆腐家常料理","ingredients_used":["豆腐"],"missing_ingredients":["蒜頭"],"steps":["切塊","拌炒"],"cooking_time_minutes":25,"note":"僅供生活參考"}'
    )
    _process_recipe_job(db=db, job=jobs[0], recipe_service=recipe_service)

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "success"
    assert job.result is not None
    assert "豆腐" in job.result["ingredients_used"]


def test_auto_from_pantry_failed_when_no_available_items_with_chinese_message() -> None:
    """auto_from_pantry 無可用食材時應 failed 且帶中文訊息。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        PantryItem(
            user_id=1,
            name="過期牛奶",
            category="乳品",
            quantity=1,
            unit="瓶",
            expiration_date=date.today() - timedelta(days=1),
            storage_location="fridge",
            note=None,
        )
    )
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={"recommendation_mode": "auto_from_pantry"},
        )
    )
    db.commit()

    jobs = _claim_pending_jobs(db=db, batch_size=5, enabled_job_types=["recipe_recommendation"])
    recipe_service = _make_recipe_service(
        '{"recipe_name":"測試","ingredients_used":[],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":10,"note":"僅供生活參考"}'
    )
    _process_recipe_job(db=db, job=jobs[0], recipe_service=recipe_service)

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "failed"
    assert job.error_message is not None
    assert "目前沒有可用食材" in job.error_message


def test_worker_does_not_cross_user_use_pantry_data() -> None:
    """worker 在 auto_from_pantry 僅使用該 job user_id 的 pantry 資料。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    _create_user(db, user_id=2, email="u2@example.com")

    db.add(
        PantryItem(
            user_id=2,
            name="他人食材",
            category="蔬菜",
            quantity=1,
            unit="把",
            expiration_date=date.today() + timedelta(days=2),
            storage_location="fridge",
            note=None,
        )
    )
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={"recommendation_mode": "auto_from_pantry"},
        )
    )
    db.commit()

    jobs = _claim_pending_jobs(db=db, batch_size=5, enabled_job_types=["recipe_recommendation"])
    recipe_service = _make_recipe_service(
        '{"recipe_name":"測試","ingredients_used":[],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":10,"note":"僅供生活參考"}'
    )
    _process_recipe_job(db=db, job=jobs[0], recipe_service=recipe_service)

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "failed"
    assert "目前沒有可用食材" in (job.error_message or "")


def test_invalid_llm_payload_should_fail_with_chinese_error_message() -> None:
    """LLM 回傳非 JSON 時，job 應 failed 並帶中文錯誤。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={
                "recommendation_mode": "selected_items",
                "resolved_pantry_items": [{"id": 10, "name": "雞蛋", "status": "normal"}],
            },
        )
    )
    db.commit()

    jobs = _claim_pending_jobs(db=db, batch_size=5, enabled_job_types=["recipe_recommendation"])
    recipe_service = _make_recipe_service("這不是 JSON")
    _process_recipe_job(db=db, job=jobs[0], recipe_service=recipe_service)

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "failed"
    assert "無法解析" in (job.error_message or "")


def test_worker_claims_only_enabled_job_types() -> None:
    """worker 只會 claim 啟用清單中的 job_type。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={"recommendation_mode": "selected_items", "resolved_pantry_items": [{"id": 1, "name": "蛋", "status": "normal"}]},
        )
    )
    db.add(
        AiJob(
            user_id=1,
            job_type="ingredient_photo",
            status="pending",
            input_snapshot={},
        )
    )
    db.commit()

    claimed = _claim_pending_jobs(db=db, batch_size=10, enabled_job_types=["recipe_recommendation"])
    assert len(claimed) == 1
    assert claimed[0].job_type == "recipe_recommendation"

    all_jobs = db.query(AiJob).order_by(AiJob.id.asc()).all()
    assert all_jobs[0].status == "running"
    assert all_jobs[1].status == "pending"


def test_worker_does_not_claim_jobs_outside_enabled_job_types() -> None:
    """worker 啟用 job_type 不包含 recipe 時，不會 claim recipe job。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="recipe_recommendation",
            status="pending",
            input_snapshot={"recommendation_mode": "auto_from_pantry"},
        )
    )
    db.commit()

    claimed = _claim_pending_jobs(db=db, batch_size=10, enabled_job_types=["ingredient_photo"])
    assert claimed == []

    job = db.query(AiJob).one()
    assert job.status == "pending"


def test_worker_claims_ingredient_photo_when_enabled() -> None:
    """enabled_job_types 包含 ingredient_photo 時應可 claim。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="ingredient_photo",
            status="pending",
            input_snapshot={"image_path": "uploads/ingredient_photos/mock.jpg"},
        )
    )
    db.commit()

    claimed = _claim_pending_jobs(db=db, batch_size=10, enabled_job_types=["ingredient_photo"])
    assert len(claimed) == 1
    assert claimed[0].job_type == "ingredient_photo"
    assert claimed[0].status == "running"


def test_mock_ingredient_photo_job_success_and_no_pantry_write() -> None:
    """ingredient_photo mock job 成功寫入候選，不可直接寫入 pantry。"""
    db = _make_session()
    _create_user(db, user_id=1, email="u1@example.com")
    db.add(
        AiJob(
            user_id=1,
            job_type="ingredient_photo",
            status="pending",
            input_snapshot={"image_path": "uploads/ingredient_photos/mock.jpg"},
        )
    )
    db.commit()

    claimed = _claim_pending_jobs(db=db, batch_size=10, enabled_job_types=["ingredient_photo"])
    assert len(claimed) == 1
    _process_ingredient_photo_job(db=db, job=claimed[0])

    job = db.get(AiJob, claimed[0].id)
    assert job is not None
    assert job.status == "success"
    assert job.result is not None
    assert "candidate_items" in job.result
    assert len(job.result["candidate_items"]) >= 1

    pantry_count = db.query(PantryItem).count()
    assert pantry_count == 0
