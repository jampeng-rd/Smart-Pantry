"""AI job DB polling worker（Phase 08-2 LangChain + Ollama）。"""

from __future__ import annotations

import argparse
import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, asc, or_, select
from sqlalchemy.orm import Session, sessionmaker

from ai_server.app.clients.ingredient_vision_client import OllamaIngredientVisionClient
from ai_server.app.clients.recipe_llm_client import OllamaRecipeLlmClient
from ai_server.app.infra.settings import get_settings
from ai_server.app.services.ingredient_photo_recognition_service import (
    INGREDIENT_PHOTO_TIMEOUT_MESSAGE,
    IngredientPhotoRecognitionError,
    IngredientPhotoRecognitionService,
)
from ai_server.app.services.recipe_recommendation_service import RecipeRecommendationError, RecipeRecommendationService
from backend.app.domain.models.ai_job_model import AiJob
from backend.app.domain.models.pantry_item_model import PantryItem
from backend.app.infra.database import engine as backend_engine
from backend.app.infra.repository.ai_job_repository import AiJobRepository

LOGGER = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=backend_engine, autoflush=False, autocommit=False, class_=Session)


def _get_item_status(expiration_date: date | None) -> str:
    """依 expiration_date 回傳食材狀態。"""
    if expiration_date is None:
        return "normal"

    today = date.today()
    soon_end = today + timedelta(days=3)
    if expiration_date < today:
        return "expired"
    if today <= expiration_date <= soon_end:
        return "expiring_soon"
    return "normal"


def _to_pantry_snapshot(item: PantryItem) -> dict[str, Any]:
    """將 pantry model 轉為可寫入 job result 的簡化格式。"""
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "quantity": float(item.quantity),
        "unit": item.unit,
        "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None,
        "status": _get_item_status(item.expiration_date),
    }


def _get_auto_mode_candidates(db: Session, user_id: int) -> list[dict[str, Any]]:
    """查詢 auto_from_pantry 模式可用食材（normal / expiring_soon，排除 expired）。"""
    today = date.today()
    statement = (
        select(PantryItem)
        .where(
            PantryItem.user_id == user_id,
            or_(PantryItem.expiration_date.is_(None), PantryItem.expiration_date >= today),
        )
        .order_by(
            asc(PantryItem.expiration_date.is_(None)),
            asc(PantryItem.expiration_date),
            asc(PantryItem.id),
        )
    )
    return [_to_pantry_snapshot(item) for item in db.execute(statement).scalars().all()]


def _claim_pending_jobs(db: Session, batch_size: int, enabled_job_types: list[str]) -> list[AiJob]:
    """一次 claim 一批 pending jobs，狀態改為 running。"""
    return AiJobRepository(db).claim_pending_jobs(batch_size=batch_size, job_types=enabled_job_types)


def _fail_stale_running_jobs(db: Session, enabled_job_types: list[str], timeout_seconds: int) -> int:
    """將超過逾時門檻的 running jobs 標記為 failed，避免永久卡住。"""
    if not enabled_job_types or timeout_seconds <= 0:
        return 0

    stale_before = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
    statement = select(AiJob).where(
        and_(
            AiJob.status == "running",
            AiJob.job_type.in_(enabled_job_types),
            AiJob.started_at.is_not(None),
            AiJob.started_at <= stale_before,
        )
    )
    stale_jobs = list(db.execute(statement).scalars().all())
    if not stale_jobs:
        return 0

    now = datetime.now(timezone.utc)
    for job in stale_jobs:
        job.status = "failed"
        job.error_message = INGREDIENT_PHOTO_TIMEOUT_MESSAGE
        job.finished_at = now
        db.add(job)
    db.commit()
    LOGGER.warning("marked stale running jobs as failed count=%s enabled_job_types=%s", len(stale_jobs), enabled_job_types)
    return len(stale_jobs)


def _process_recipe_job(db: Session, job: AiJob, recipe_service: RecipeRecommendationService) -> None:
    """處理單筆 recipe_recommendation job，並寫回 success/failed。"""
    try:
        snapshot = job.input_snapshot or {}
        mode = snapshot.get("recommendation_mode")

        if mode == "selected_items":
            resolved_items = snapshot.get("resolved_pantry_items") or []
            if not resolved_items:
                raise ValueError("selected_items 模式缺少可用食材，請重新選擇食材後再試。")
            candidates = [item for item in resolved_items if item.get("status") in {"normal", "expiring_soon"}]
            if not candidates:
                raise ValueError("目前選擇的食材皆不可用於推薦，請改選未過期食材。")
        elif mode == "auto_from_pantry":
            candidates = _get_auto_mode_candidates(db=db, user_id=job.user_id)
            if not candidates:
                raise ValueError("目前沒有可用食材可供推薦，請先新增未過期食材。")
        else:
            raise ValueError("不支援的食譜推薦模式，請重新建立任務。")

        job.result = recipe_service.recommend(input_snapshot=snapshot, pantry_items=candidates)
        job.status = "success"
        job.error_message = None
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
    except RecipeRecommendationError as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
    except ValueError as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
    except Exception:
        LOGGER.exception("recipe job processing failed unexpectedly, job_id=%s", job.id)
        job.status = "failed"
        job.error_message = "系統處理食譜推薦任務時發生問題，請稍後再試。"
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()


def _process_ingredient_photo_job(db: Session, job: AiJob, recognition_service: IngredientPhotoRecognitionService) -> None:
    """處理單筆 ingredient_photo job，並寫回 success/failed。"""
    started_at = time.monotonic()
    LOGGER.info("start ingredient_photo job processing job_id=%s", job.id)
    try:
        snapshot = job.input_snapshot or {}
        image_path = snapshot.get("image_path")
        LOGGER.info("calling vision model for ingredient_photo job_id=%s", job.id)
        job.result = recognition_service.recognize(image_path=image_path or "")
        elapsed = time.monotonic() - started_at
        LOGGER.info("vision completed for ingredient_photo job_id=%s elapsed_seconds=%.2f", job.id, elapsed)
        job.status = "success"
        job.error_message = None
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
        LOGGER.info("ingredient_photo job commit success job_id=%s", job.id)
    except IngredientPhotoRecognitionError as exc:
        LOGGER.warning("ingredient_photo recognition failed job_id=%s error=%s", job.id, str(exc))
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
        LOGGER.info("ingredient_photo job commit failed job_id=%s", job.id)
    except Exception:
        LOGGER.exception("ingredient photo job processing failed unexpectedly, job_id=%s", job.id)
        job.status = "failed"
        job.error_message = "系統處理食材辨識任務時發生問題，請稍後再試。"
        job.finished_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()
        LOGGER.info("ingredient_photo job commit failed job_id=%s", job.id)


def _parse_job_types_arg() -> list[str] | None:
    """解析 CLI --job-types 參數。"""
    parser = argparse.ArgumentParser(description="Smart Pantry AI DB polling worker")
    parser.add_argument("--job-types", type=str, default=None, help="逗號分隔 job types，例如 recipe_recommendation,ingredient_photo")
    args = parser.parse_args()
    if not args.job_types:
        return None
    parsed = [job_type.strip() for job_type in args.job_types.split(",") if job_type.strip()]
    return parsed or None


def _resolve_enabled_job_types(cli_job_types: list[str] | None) -> list[str]:
    """決定 worker 啟用的 job types（CLI 優先，其次 env）。"""
    settings = get_settings()
    if cli_job_types is not None:
        return cli_job_types
    return settings.get_ai_worker_job_types()


def poll_once(enabled_job_types: list[str] | None = None) -> None:
    """執行一次 polling 週期並處理一批 pending jobs。"""
    settings = get_settings()
    resolved_job_types = enabled_job_types if enabled_job_types is not None else settings.get_ai_worker_job_types()
    recipe_service = RecipeRecommendationService(llm_client=OllamaRecipeLlmClient())
    recognition_service = IngredientPhotoRecognitionService(vision_client=OllamaIngredientVisionClient())
    with SessionLocal() as db:
        _fail_stale_running_jobs(
            db=db,
            enabled_job_types=resolved_job_types,
            timeout_seconds=settings.ai_job_timeout_seconds,
        )
        jobs = _claim_pending_jobs(
            db=db,
            batch_size=settings.ai_worker_batch_size,
            enabled_job_types=resolved_job_types,
        )
        if not jobs:
            return
        LOGGER.info("poll once claimed %s jobs, enabled_job_types=%s", len(jobs), resolved_job_types)
        for job in jobs:
            if job.job_type == "recipe_recommendation":
                _process_recipe_job(db=db, job=job, recipe_service=recipe_service)
                continue
            if job.job_type == "ingredient_photo":
                _process_ingredient_photo_job(db=db, job=job, recognition_service=recognition_service)
                continue

            job.status = "failed"
            job.error_message = f"worker 尚未支援處理 job_type={job.job_type}"
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()
            LOGGER.warning("unsupported job_type claimed and marked as failed, job_id=%s, job_type=%s", job.id, job.job_type)


def run_forever(enabled_job_types: list[str] | None = None) -> None:
    """持續執行 DB polling worker。"""
    settings = get_settings()
    resolved_job_types = enabled_job_types if enabled_job_types is not None else settings.get_ai_worker_job_types()
    LOGGER.info(
        "ai worker started, poll_interval=%s, batch_size=%s, enabled_job_types=%s",
        settings.ai_worker_poll_interval_seconds,
        settings.ai_worker_batch_size,
        resolved_job_types,
    )
    while True:
        poll_once(enabled_job_types=resolved_job_types)
        time.sleep(settings.ai_worker_poll_interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_forever(enabled_job_types=_resolve_enabled_job_types(_parse_job_types_arg()))
