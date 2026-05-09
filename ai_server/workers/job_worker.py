"""AI job DB polling worker（Phase 08-1 mock recipe handler）。"""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, asc, or_, select
from sqlalchemy.orm import Session, sessionmaker

from ai_server.app.infra.settings import get_settings
from backend.app.domain.models.ai_job_model import AiJob
from backend.app.domain.models.pantry_item_model import PantryItem
from backend.app.infra.database import engine as backend_engine

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


def _build_mock_recipe_result(job: AiJob, pantry_items: list[dict[str, Any]]) -> dict[str, Any]:
    """建立 mock recipe recommendation 結果。"""
    item_names = [item["name"] for item in pantry_items]
    picked_ingredients = item_names[: min(3, len(item_names))]

    cooking_time_minutes = job.input_snapshot.get("cooking_time_minutes") or 20
    missing_ingredients = ["鹽", "食用油"]

    return {
        "recipe_name": f"{picked_ingredients[0] if picked_ingredients else '家常'}快炒",
        "ingredients_used": picked_ingredients,
        "missing_ingredients": missing_ingredients,
        "steps": [
            "將主要食材清洗並切成適合入口大小。",
            "熱鍋後加入少量食用油，先下較耐炒食材。",
            "加入其餘食材與調味料拌炒至熟，起鍋即可。",
        ],
        "cooking_time_minutes": cooking_time_minutes,
        "note": "此為 Phase 08-1 Mock 結果，僅供流程驗證與 UI 串接測試。",
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


def _claim_pending_jobs(db: Session, batch_size: int) -> list[AiJob]:
    """一次 claim 一批 pending recipe jobs，狀態改為 running。"""
    statement = (
        select(AiJob)
        .where(and_(AiJob.status == "pending", AiJob.job_type == "recipe_recommendation"))
        .order_by(asc(AiJob.created_at), asc(AiJob.id))
        .limit(batch_size)
    )
    jobs = list(db.execute(statement).scalars().all())
    now = datetime.now(timezone.utc)
    claimed: list[AiJob] = []
    for job in jobs:
        current = db.get(AiJob, job.id)
        if current is None or current.status != "pending":
            continue
        current.status = "running"
        current.started_at = now
        current.finished_at = None
        current.error_message = None
        current.result = None
        claimed.append(current)
    db.commit()
    return claimed


def _process_recipe_job(db: Session, job: AiJob) -> None:
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

        job.result = _build_mock_recipe_result(job=job, pantry_items=candidates)
        job.status = "success"
        job.error_message = None
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


def poll_once() -> None:
    """執行一次 polling 週期並處理一批 pending recipe jobs。"""
    settings = get_settings()
    with SessionLocal() as db:
        jobs = _claim_pending_jobs(db=db, batch_size=settings.ai_worker_batch_size)
        if not jobs:
            return
        LOGGER.info("poll once claimed %s recipe jobs", len(jobs))
        for job in jobs:
            _process_recipe_job(db=db, job=job)


def run_forever() -> None:
    """持續執行 DB polling worker。"""
    settings = get_settings()
    LOGGER.info("ai worker started, poll_interval=%s", settings.ai_worker_poll_interval_seconds)
    while True:
        poll_once()
        time.sleep(settings.ai_worker_poll_interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_forever()
