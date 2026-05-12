"""到期提醒 runner 測試。"""

from datetime import datetime, timezone

import pytest

from backend.app.jobs.expiration_email_runner import resolve_send_window, run_once


def test_resolve_send_window_morning() -> None:
    """上午應判定為 morning_08。"""
    assert resolve_send_window(datetime(2026, 5, 13, 8, 0, tzinfo=timezone.utc)) == "morning_08"


def test_resolve_send_window_evening() -> None:
    """下午應判定為 evening_17。"""
    assert resolve_send_window(datetime(2026, 5, 13, 17, 0, tzinfo=timezone.utc)) == "evening_17"


def test_runner_should_execute_successfully(monkeypatch: pytest.MonkeyPatch) -> None:
    """runner 應可正常執行並回傳摘要。"""
    class FakeResult:
        """測試用執行摘要。"""

        total_users = 3
        success_count = 2
        failed_count = 1
        skipped_none = 0
        skipped_duplicate = 0
        skipped_no_items = 0

    class FakeSessionContext:
        """測試用 DB context manager。"""

        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("backend.app.jobs.expiration_email_runner.SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr("backend.app.jobs.expiration_email_runner._run_once_with_session", lambda db, scheduled_date, send_window: FakeResult())

    summary = run_once(now=datetime(2026, 5, 13, 8, 0, tzinfo=timezone.utc), send_window="morning_08")

    assert summary["send_window"] == "morning_08"
    assert summary["scheduled_date"] == "2026-05-13"
    assert summary["total_users"] == 3
