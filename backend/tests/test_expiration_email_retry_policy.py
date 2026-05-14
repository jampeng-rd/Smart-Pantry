"""到期提醒 Email retry policy 測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from backend.app.infra.email_client import BaseEmailClient, EmailMessage, EmailSendResult
from backend.app.services.expiration_email_reminder_service import ExpirationEmailReminderService


@dataclass
class FakeUser:
    """測試用使用者。"""

    id: int
    email: str
    display_name: str


@dataclass
class FakePreference:
    """測試用偏好設定。"""

    expiration_email_reminder_days: str


@dataclass
class FakePantryItem:
    """測試用食材。"""

    id: int
    user_id: int
    name: str
    expiration_date: date
    quantity: int = 1
    unit: str = "份"
    storage_location: str | None = None


@dataclass
class FakeDelivery:
    """測試用寄送紀錄。"""

    id: int
    user_id: int
    scheduled_date: date
    send_window: str
    reminder_days: str
    item_ids: list[int]
    email_to: str
    status: str = "pending"
    final_status: str = "failed"
    attempt_count: int = 0
    last_error_message: str | None = None
    last_attempt_at: datetime | None = None
    error_message: str | None = None


class FakeRepository:
    """測試用 repository。"""

    def __init__(self) -> None:
        self.users = [(FakeUser(id=1, email="user@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
        self.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
        self.deliveries: list[FakeDelivery] = []
        self._seq = 1

    def list_users_with_preferences(self):
        return self.users

    def list_items_by_user_and_expiration_date(self, user_id: int, expiration_date: date):
        return [x for x in self.items if x.user_id == user_id and x.expiration_date == expiration_date]

    def has_success_delivery(self, user_id: int, scheduled_date: date, send_window: str) -> bool:
        return any(x.user_id == user_id and x.scheduled_date == scheduled_date and x.send_window == send_window and x.status == "success" for x in self.deliveries)

    def create_delivery(self, user_id: int, scheduled_date: date, send_window: str, reminder_days: str, item_ids: list[int], email_to: str):
        row = FakeDelivery(
            id=self._seq,
            user_id=user_id,
            scheduled_date=scheduled_date,
            send_window=send_window,
            reminder_days=reminder_days,
            item_ids=item_ids,
            email_to=email_to,
        )
        self._seq += 1
        self.deliveries.append(row)
        return row

    def mark_delivery_success(self, row: FakeDelivery, sent_at: datetime, attempt_count: int):
        row.status = "success"
        row.final_status = "success"
        row.attempt_count = attempt_count
        row.last_attempt_at = sent_at
        row.last_error_message = None
        row.error_message = None
        return row

    def mark_delivery_failed(self, row: FakeDelivery, error_message: str, attempt_count: int, attempted_at: datetime, permanent: bool):
        row.status = "failed"
        row.final_status = "permanent_failed" if permanent else "failed"
        row.attempt_count = attempt_count
        row.last_attempt_at = attempted_at
        row.last_error_message = error_message
        row.error_message = error_message
        return row

    def delete_old_deliveries_before(self, cutoff_scheduled_date: date):
        return 0


class SequenceEmailClient(BaseEmailClient):
    """依序回傳結果的 email client。"""

    def __init__(self, results: list[EmailSendResult]):
        self.results = results
        self.index = 0

    def send_email(self, message: EmailMessage) -> EmailSendResult:
        current = self.results[min(self.index, len(self.results) - 1)]
        self.index += 1
        return current


def test_retry_disabled_when_max_attempts_zero() -> None:
    """EMAIL_RETRY_MAX_ATTEMPTS=0 時不應重試。"""
    repo = FakeRepository()
    client = SequenceEmailClient([
        EmailSendResult(success=False, should_retry=True, error_category="timeout", error_message="timeout"),
    ])
    sleeps: list[int] = []
    service = ExpirationEmailReminderService(repo, client, retry_max_attempts=0, sleep_fn=lambda sec: sleeps.append(sec))

    result = service.run_for_window(date(2026, 5, 13), "morning_08")

    assert result.retry_count == 0
    assert result.permanent_failed_count == 1
    assert repo.deliveries[0].attempt_count == 1
    assert repo.deliveries[0].final_status == "permanent_failed"
    assert sleeps == []


def test_retry_backoff_should_be_5_15_30() -> None:
    """重試 backoff 應為 5、15、30 秒。"""
    repo = FakeRepository()
    client = SequenceEmailClient([
        EmailSendResult(success=False, should_retry=True, error_category="timeout", error_message="timeout-1"),
        EmailSendResult(success=False, should_retry=True, error_category="network_error", error_message="timeout-2"),
        EmailSendResult(success=False, should_retry=True, error_category="provider_5xx", error_message="timeout-3"),
        EmailSendResult(success=True),
    ])
    sleeps: list[int] = []
    service = ExpirationEmailReminderService(repo, client, retry_max_attempts=3, sleep_fn=lambda sec: sleeps.append(sec))

    result = service.run_for_window(date(2026, 5, 13), "morning_08")

    assert result.retry_count == 3
    assert result.success_count == 1
    assert sleeps == [5, 15, 30]
    assert repo.deliveries[0].attempt_count == 4


def test_retry_should_stop_as_permanent_failed_after_max_attempts() -> None:
    """超過重試次數後應 permanent_failed。"""
    repo = FakeRepository()
    client = SequenceEmailClient([
        EmailSendResult(success=False, should_retry=True, error_category="provider_5xx", error_message="e1"),
        EmailSendResult(success=False, should_retry=True, error_category="provider_5xx", error_message="e2"),
    ])
    service = ExpirationEmailReminderService(repo, client, retry_max_attempts=1, sleep_fn=lambda sec: None)

    result = service.run_for_window(date(2026, 5, 13), "morning_08")

    assert result.retry_count == 1
    assert result.permanent_failed_count == 1
    assert repo.deliveries[0].attempt_count == 2
    assert repo.deliveries[0].final_status == "permanent_failed"


def test_non_retryable_error_should_be_permanent_failed() -> None:
    """不可重試錯誤應直接 permanent_failed。"""
    repo = FakeRepository()
    client = SequenceEmailClient([
        EmailSendResult(success=False, should_retry=False, error_category="invalid_configuration", error_message="invalid config"),
    ])
    service = ExpirationEmailReminderService(repo, client, retry_max_attempts=3, sleep_fn=lambda sec: None)

    result = service.run_for_window(date(2026, 5, 13), "morning_08")

    assert result.retry_count == 0
    assert result.permanent_failed_count == 1
    assert repo.deliveries[0].final_status == "permanent_failed"


def test_monitoring_log_should_not_include_secret(caplog) -> None:
    """monitoring log 不可包含 secret。"""
    repo = FakeRepository()
    client = SequenceEmailClient([
        EmailSendResult(success=False, should_retry=True, error_category="timeout", error_message="token=secret-abc"),
        EmailSendResult(success=False, should_retry=False, error_category="provider_4xx", error_message="bad request"),
    ])
    service = ExpirationEmailReminderService(repo, client, retry_max_attempts=1, sleep_fn=lambda sec: None)

    with caplog.at_level("INFO"):
        result = service.run_for_window(date(2026, 5, 13), "morning_08")

    assert result.retry_count == 1
    assert "secret-abc" not in caplog.text
