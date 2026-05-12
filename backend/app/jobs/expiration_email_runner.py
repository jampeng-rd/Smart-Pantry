"""到期 Email 提醒 runner（Phase 10-2）。"""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from backend.app.infra.database import SessionLocal
from backend.app.infra.email_client import FakeEmailClient
from backend.app.infra.repository.expiration_email_reminder_repository import ExpirationEmailReminderRepository
from backend.app.services.expiration_email_reminder_service import ExpirationEmailReminderService

LOGGER = logging.getLogger(__name__)


def resolve_send_window(now: datetime) -> str:
    """依目前時間判斷提醒時段。"""
    return "morning_08" if now.hour < 12 else "evening_17"


def run_once(now: datetime | None = None, send_window: str | None = None) -> dict[str, int | str]:
    """執行一次提醒流程，回傳摘要。"""
    current = now or datetime.now(timezone.utc)
    effective_window = send_window or resolve_send_window(current)
    scheduled_date = current.date()

    with SessionLocal() as db:
        result = _run_once_with_session(db=db, scheduled_date=scheduled_date, send_window=effective_window)

    summary = {
        "scheduled_date": scheduled_date.isoformat(),
        "send_window": effective_window,
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
    email_client = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=email_client)
    return service.run_for_window(scheduled_date=scheduled_date, send_window=send_window)


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="執行到期 Email 提醒 runner")
    parser.add_argument("--send-window", choices=["morning_08", "evening_17"], default=None)
    parser.add_argument("--scheduled-date", default=None, help="指定排程日期，格式 YYYY-MM-DD")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    now = datetime.now(timezone.utc)
    if args.scheduled_date:
        scheduled_date = date.fromisoformat(args.scheduled_date)
        now = datetime.combine(scheduled_date, datetime.min.time(), tzinfo=timezone.utc)

    run_once(now=now, send_window=args.send_window)


if __name__ == "__main__":
    main()
