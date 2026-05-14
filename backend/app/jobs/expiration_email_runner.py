"""到期 Email 提醒 runner（Phase 11-3）。"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import asdict
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from backend.app.infra.database import SessionLocal
from backend.app.infra.email_client_factory import build_email_client
from backend.app.infra.repository.expiration_email_reminder_repository import ExpirationEmailReminderRepository
from backend.app.infra.settings import get_settings
from backend.app.services.expiration_email_reminder_service import ExpirationEmailReminderService

LOGGER = logging.getLogger(__name__)
VALID_SEND_WINDOWS = {"morning_08", "evening_17"}


def resolve_send_window(now: datetime) -> str | None:
    """依目前時間判斷提醒時段；非排程時段回傳 None。"""
    if now.hour == 8:
        return "morning_08"
    if now.hour == 17:
        return "evening_17"
    return None


def resolve_scheduler_now(now: datetime | None = None) -> datetime:
    """取得排程時區下的現在時間。"""
    settings = get_settings()
    timezone_name = getattr(settings, "scheduler_timezone", "Asia/Taipei")
    scheduler_tz = ZoneInfo(timezone_name)
    if now is None:
        return datetime.now(scheduler_tz)
    return now.astimezone(scheduler_tz)


def run_once(
    now: datetime | None = None,
    send_window: str | None = None,
    scheduled_date: date | None = None,
) -> dict[str, int | str | bool]:
    """執行一次提醒流程，回傳摘要。"""
    current = resolve_scheduler_now(now)
    effective_window = send_window or resolve_send_window(current)
    effective_date = scheduled_date or current.date()

    if effective_window is None:
        summary = {
            "scheduled_date": effective_date.isoformat(),
            "send_window": "none",
            "executed": False,
            "reason": "非排程時段，僅允許 08:00 或 17:00 執行",
            "total_users": 0,
            "success_count": 0,
            "failed_count": 0,
            "skipped_none": 0,
            "skipped_duplicate": 0,
            "skipped_no_items": 0,
        }
        LOGGER.info("expiration email runner skipped summary=%s", summary)
        return summary

    if effective_window not in VALID_SEND_WINDOWS:
        raise ValueError("send_window 僅允許 morning_08 或 evening_17")

    with SessionLocal() as db:
        result = _run_once_with_session(db=db, scheduled_date=effective_date, send_window=effective_window)

    summary = {
        "scheduled_date": effective_date.isoformat(),
        "send_window": effective_window,
        "executed": True,
        "total_users": result.total_users,
        "success_count": result.success_count,
        "failed_count": result.failed_count,
        "skipped_none": result.skipped_none,
        "skipped_duplicate": result.skipped_duplicate,
        "skipped_no_items": result.skipped_no_items,
    }
    LOGGER.info("expiration email runner summary=%s", summary)
    return summary


def _run_once_with_session(db: Session, scheduled_date: date, send_window: str):
    """以指定 DB session 執行一次提醒流程。"""
    repository = ExpirationEmailReminderRepository(db=db)
    email_client = build_email_client(get_settings())
    service = ExpirationEmailReminderService(repository=repository, email_client=email_client)
    return service.run_for_window(scheduled_date=scheduled_date, send_window=send_window)


def main() -> int:
    """CLI 入口，成功回傳 0，失敗回傳非 0。"""
    parser = argparse.ArgumentParser(description="執行到期 Email 提醒 runner")
    parser.add_argument("--send-window", choices=["morning_08", "evening_17"], default=None)
    parser.add_argument("--scheduled-date", default=None, help="指定排程日期，格式 YYYY-MM-DD")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    try:
        resolved_now = resolve_scheduler_now()
        resolved_date = date.fromisoformat(args.scheduled_date) if args.scheduled_date else None
        summary = run_once(now=resolved_now, send_window=args.send_window, scheduled_date=resolved_date)
        LOGGER.info("expiration email runner completed: %s", summary)
        return 0
    except Exception:
        LOGGER.exception("expiration email runner failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
