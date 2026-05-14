"""到期提醒 runner 測試。"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from backend.app.jobs import expiration_email_runner as runner


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


def test_resolve_send_window_morning() -> None:
    """上午應判定為 morning_08。"""
    assert runner.resolve_send_window(datetime(2026, 5, 13, 8, 10, tzinfo=timezone.utc)) == "morning_08"


def test_resolve_send_window_evening() -> None:
    """下午應判定為 evening_17。"""
    assert runner.resolve_send_window(datetime(2026, 5, 13, 17, 20, tzinfo=timezone.utc)) == "evening_17"


def test_resolve_send_window_none_outside_schedule() -> None:
    """非排程時段應回傳 None。"""
    assert runner.resolve_send_window(datetime(2026, 5, 13, 10, 0, tzinfo=timezone.utc)) is None


def test_runner_auto_detect_morning(monkeypatch: pytest.MonkeyPatch) -> None:
    """不帶 send-window 時，08 點應自動使用 morning_08。"""
    monkeypatch.setattr(runner, "SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(runner, "_run_once_with_session", lambda db, scheduled_date, send_window: FakeResult())

    summary = runner.run_once(now=datetime(2026, 5, 13, 0, 5, tzinfo=timezone.utc))

    assert summary["executed"] is True
    assert summary["send_window"] == "morning_08"


def test_runner_auto_detect_evening(monkeypatch: pytest.MonkeyPatch) -> None:
    """不帶 send-window 時，17 點應自動使用 evening_17。"""
    monkeypatch.setattr(runner, "SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(runner, "_run_once_with_session", lambda db, scheduled_date, send_window: FakeResult())

    summary = runner.run_once(now=datetime(2026, 5, 13, 9, 5, tzinfo=timezone.utc))

    assert summary["executed"] is True
    assert summary["send_window"] == "evening_17"


def test_runner_should_skip_outside_schedule(monkeypatch: pytest.MonkeyPatch) -> None:
    """非排程時段應回傳明確略過訊息且不執行。"""
    called = {"value": False}

    def fake_run_once_with_session(db, scheduled_date, send_window):
        called["value"] = True
        return FakeResult()

    monkeypatch.setattr(runner, "SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(runner, "_run_once_with_session", fake_run_once_with_session)

    summary = runner.run_once(now=datetime(2026, 5, 13, 10, 0, tzinfo=timezone.utc))

    assert summary["executed"] is False
    assert summary["send_window"] == "none"
    assert called["value"] is False


def test_runner_cli_send_window_should_override_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI 指定 send-window 應覆蓋自動判斷。"""
    monkeypatch.setattr(runner, "SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(runner, "_run_once_with_session", lambda db, scheduled_date, send_window: FakeResult())

    summary = runner.run_once(now=datetime(2026, 5, 13, 10, 0, tzinfo=timezone.utc), send_window="evening_17")

    assert summary["executed"] is True
    assert summary["send_window"] == "evening_17"


def test_runner_should_accept_scheduled_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """可指定 scheduled_date。"""
    monkeypatch.setattr(runner, "SessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(runner, "_run_once_with_session", lambda db, scheduled_date, send_window: FakeResult())

    summary = runner.run_once(
        now=datetime(2026, 5, 13, 8, 0, tzinfo=timezone.utc),
        send_window="morning_08",
        scheduled_date=date(2026, 5, 20),
    )

    assert summary["scheduled_date"] == "2026-05-20"


def test_runner_main_should_return_non_zero_on_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """runner 發生錯誤時應回傳非 0。"""

    def fake_run_once(*args, **kwargs):
        raise RuntimeError("service down")

    monkeypatch.setattr(runner, "run_once", fake_run_once)
    monkeypatch.setattr(runner, "resolve_scheduler_now", lambda now=None: datetime(2026, 5, 13, 8, 0, tzinfo=timezone.utc))
    monkeypatch.setattr("sys.argv", ["expiration_email_runner"])

    assert runner.main() != 0
