"""到期 Email 提醒服務測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from backend.app.infra.email_client import FakeEmailClient
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
    """測試用食材資料。"""

    id: int
    user_id: int
    name: str
    expiration_date: date | None


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
    status: str
    sent_at: datetime | None = None
    error_message: str | None = None


class FakeExpirationEmailReminderRepository:
    """以記憶體模擬提醒資料存取層。"""

    def __init__(self) -> None:
        """初始化假資料。"""
        self.users: list[tuple[FakeUser, FakePreference | None]] = []
        self.items: list[FakePantryItem] = []
        self.deliveries: list[FakeDelivery] = []
        self._delivery_seq = 1

    def list_users_with_preferences(self) -> list[tuple[FakeUser, FakePreference | None]]:
        """列出使用者與偏好。"""
        return self.users

    def list_items_by_user_and_expiration_date(self, user_id: int, expiration_date: date) -> list[FakePantryItem]:
        """依 user 與到期日查詢食材。"""
        return [item for item in self.items if item.user_id == user_id and item.expiration_date == expiration_date]

    def has_success_delivery(self, user_id: int, scheduled_date: date, send_window: str) -> bool:
        """查詢是否已有成功寄送。"""
        return any(
            row.user_id == user_id
            and row.scheduled_date == scheduled_date
            and row.send_window == send_window
            and row.status == "success"
            for row in self.deliveries
        )

    def create_delivery(
        self,
        user_id: int,
        scheduled_date: date,
        send_window: str,
        reminder_days: str,
        item_ids: list[int],
        email_to: str,
    ) -> FakeDelivery:
        """建立 pending 寄送紀錄。"""
        row = FakeDelivery(
            id=self._delivery_seq,
            user_id=user_id,
            scheduled_date=scheduled_date,
            send_window=send_window,
            reminder_days=reminder_days,
            item_ids=item_ids,
            email_to=email_to,
            status="pending",
        )
        self.deliveries.append(row)
        self._delivery_seq += 1
        return row

    def mark_delivery_success(self, row: FakeDelivery, sent_at: datetime) -> FakeDelivery:
        """標記成功。"""
        row.status = "success"
        row.sent_at = sent_at
        row.error_message = None
        return row

    def mark_delivery_failed(self, row: FakeDelivery, error_message: str) -> FakeDelivery:
        """標記失敗。"""
        row.status = "failed"
        row.error_message = error_message
        return row


def test_none_preference_should_not_send() -> None:
    """none 設定不應寄送。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="none"))]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 0
    assert result.skipped_none == 1
    assert len(repository.deliveries) == 0


def test_reminder_days_1_should_send_correct_items() -> None:
    """1 天提醒應只抓 scheduled_date+1。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [
        FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14)),
        FakePantryItem(id=2, user_id=1, name="雞蛋", expiration_date=date(2026, 5, 16)),
    ]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    assert len(fake_email.sent_messages) == 1
    assert "牛奶" in fake_email.sent_messages[0].content_text
    assert "雞蛋" not in fake_email.sent_messages[0].content_text


def test_reminder_days_3_should_send_correct_items() -> None:
    """3 天提醒應只抓 scheduled_date+3。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="3"))]
    repository.items = [
        FakePantryItem(id=1, user_id=1, name="豆腐", expiration_date=date(2026, 5, 16)),
        FakePantryItem(id=2, user_id=1, name="優格", expiration_date=date(2026, 5, 14)),
    ]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    assert len(fake_email.sent_messages) == 1
    assert "豆腐" in fake_email.sent_messages[0].content_text
    assert "優格" not in fake_email.sent_messages[0].content_text


def test_morning_duplicate_protection() -> None:
    """morning_08 同日同使用者成功寄送不可重複。"""
    repository = FakeExpirationEmailReminderRepository()
    user = FakeUser(id=1, email="u1@example.com", display_name="小明")
    repository.users = [(user, FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 13),
            send_window="morning_08",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        )
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.skipped_duplicate == 1
    assert result.success_count == 0


def test_evening_duplicate_protection() -> None:
    """evening_17 同日同使用者成功寄送不可重複。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 13),
            send_window="evening_17",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        )
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="evening_17")

    assert result.skipped_duplicate == 1
    assert result.success_count == 0


def test_fake_email_success() -> None:
    """fake email 成功時應寫 success。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    assert repository.deliveries[0].status == "success"


def test_fake_email_failed_should_write_error() -> None:
    """fake email 失敗時應寫 failed 與 error_message。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient(force_fail=True))

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.failed_count == 1
    assert repository.deliveries[0].status == "failed"
    assert repository.deliveries[0].error_message is not None


def test_should_not_cross_user_id() -> None:
    """不可跨使用者讀取食材。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [
        (FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1")),
        (FakeUser(id=2, email="u2@example.com", display_name="小美"), FakePreference(expiration_email_reminder_days="1")),
    ]
    repository.items = [
        FakePantryItem(id=1, user_id=2, name="別人的牛奶", expiration_date=date(2026, 5, 14)),
    ]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    assert len(fake_email.sent_messages) == 1
    assert fake_email.sent_messages[0].to_email == "u2@example.com"


def test_no_matching_items_should_not_send() -> None:
    """沒有符合到期日食材時不寄送。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 20))]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 0
    assert result.skipped_no_items == 1
    assert len(fake_email.sent_messages) == 0
