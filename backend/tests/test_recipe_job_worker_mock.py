"""Phase 08-1 recipe mock worker 單元測試。"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ai_server.workers.job_worker import _claim_pending_jobs, _process_recipe_job
from backend.app.domain.models import AiJob, Base, PantryItem, User


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

    jobs = _claim_pending_jobs(db=db, batch_size=5)
    assert len(jobs) == 1
    _process_recipe_job(db=db, job=jobs[0])

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

    jobs = _claim_pending_jobs(db=db, batch_size=5)
    _process_recipe_job(db=db, job=jobs[0])

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

    jobs = _claim_pending_jobs(db=db, batch_size=5)
    _process_recipe_job(db=db, job=jobs[0])

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

    jobs = _claim_pending_jobs(db=db, batch_size=5)
    _process_recipe_job(db=db, job=jobs[0])

    job = db.get(AiJob, jobs[0].id)
    assert job is not None
    assert job.status == "failed"
    assert "目前沒有可用食材" in (job.error_message or "")


def test_worker_module_has_no_ollama_usage() -> None:
    """本階段 worker 模組不應呼叫 Ollama。"""
    source_text = open("ai_server/workers/job_worker.py", "r", encoding="utf-8").read()
    assert "ollama" not in source_text.lower()
    assert "chatollama" not in source_text.lower()

