"""到期 Email 提醒服務測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from backend.app.infra.email_client import FakeEmailClient, GmailSmtpEmailClient
from backend.app.services.expiration_email_reminder_service import ExpirationEmailReminderService

EXPECTED_FOOTER = "此信件由系統自動發送，無需回覆。"


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
    quantity: int | float = 1
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
    status: str
    final_status: str = "failed"
    error_category: str | None = None
    attempt_count: int = 0
    last_error_message: str | None = None
    last_attempt_at: datetime | None = None
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
        self.cleanup_cutoff_dates: list[date] = []

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

    def mark_delivery_success(self, row: FakeDelivery, sent_at: datetime, attempt_count: int) -> FakeDelivery:
        """標記成功。"""
        row.status = "success"
        row.final_status = "success"
        row.attempt_count = attempt_count
        row.last_attempt_at = sent_at
        row.last_error_message = None
        row.sent_at = sent_at
        row.error_message = None
        return row

    def mark_delivery_failed(
        self,
        row: FakeDelivery,
        error_message: str,
        error_category: str | None,
        attempt_count: int,
        attempted_at: datetime,
        permanent: bool,
    ) -> FakeDelivery:
        """標記失敗。"""
        row.status = "failed"
        row.final_status = "permanent_failed" if permanent else "failed"
        row.error_category = error_category
        row.attempt_count = attempt_count
        row.last_attempt_at = attempted_at
        row.last_error_message = error_message
        row.error_message = error_message
        return row

    def delete_old_deliveries_before(self, cutoff_scheduled_date: date) -> int:
        """刪除 scheduled_date 早於 cutoff 的寄送紀錄。"""
        self.cleanup_cutoff_dates.append(cutoff_scheduled_date)
        before = len(self.deliveries)
        self.deliveries = [row for row in self.deliveries if row.scheduled_date >= cutoff_scheduled_date]
        return before - len(self.deliveries)


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
    sent = fake_email.sent_messages[0]
    assert sent.subject == "【智慧食材保存系統】食材到期提醒"
    assert "小明 您好：" in sent.content_text
    assert "以下是 2026-05-14 即將到期的食材：" in sent.content_text
    assert "食材名稱 | 數量 | 單位 | 保存位置" in sent.content_text
    assert "到期日" not in sent.content_text
    assert "牛奶 | 1 | 份 | 未設定" in sent.content_text
    assert "雞蛋" not in sent.content_text
    assert sent.content_text.endswith(EXPECTED_FOOTER)
    assert sent.content_html is not None
    assert "<table" in sent.content_html
    assert "<th" in sent.content_html
    assert "食材名稱" in sent.content_html
    assert "數量" in sent.content_html
    assert "單位" in sent.content_html
    assert "保存位置" in sent.content_html
    assert EXPECTED_FOOTER in sent.content_html
    assert "無需回信" not in sent.content_text
    assert "無需回信" not in sent.content_html
    assert "無需回覆，謝謝您" not in sent.content_text
    assert "無需回覆，謝謝您" not in sent.content_html
    assert "display:none" not in sent.content_html
    assert "max-height:0" not in sent.content_html
    assert "opacity:0" not in sent.content_html
    assert "overflow:hidden" not in sent.content_html
    assert f"</table><p style=\"margin:14px 0 0 0;\">{EXPECTED_FOOTER}</p>" in sent.content_html
    html_after_table = sent.content_html.split("</table>", maxsplit=1)[1]
    assert "<!--" not in html_after_table
    assert "<hr" not in html_after_table
    assert "<div" not in html_after_table


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
    sent = fake_email.sent_messages[0]
    assert "豆腐 | 1 | 份 | 未設定" in sent.content_text
    assert "優格" not in sent.content_text


def test_email_body_should_show_storage_location_when_present_and_fallback_when_empty() -> None:
    """信件內容應包含欄位，並在保存位置空值時顯示未設定。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [
        FakePantryItem(
            id=1,
            user_id=1,
            name="胡蘿蔔",
            quantity=1,
            unit="份",
            storage_location="冷藏",
            expiration_date=date(2026, 5, 14),
        ),
        FakePantryItem(
            id=2,
            user_id=1,
            name="番茄",
            quantity=2,
            unit="份",
            storage_location="",
            expiration_date=date(2026, 5, 14),
        ),
    ]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    sent = fake_email.sent_messages[0]
    assert "胡蘿蔔 | 1 | 份 | 冷藏" in sent.content_text
    assert "番茄 | 2 | 份 | 未設定" in sent.content_text
    assert sent.content_html is not None
    assert "胡蘿蔔" in sent.content_html
    assert "番茄" in sent.content_html
    assert "未設定" in sent.content_html


def test_email_body_should_format_quantity_without_trailing_zeroes() -> None:
    """數量顯示應移除整數小數位，非整數保留必要小數。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="Jam"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [
        FakePantryItem(
            id=1,
            user_id=1,
            name="胡蘿蔔",
            quantity=1.00,
            unit="份",
            storage_location="冰箱",
            expiration_date=date(2026, 5, 14),
        ),
        FakePantryItem(
            id=2,
            user_id=1,
            name="番茄",
            quantity=1.50,
            unit="份",
            storage_location="冰箱",
            expiration_date=date(2026, 5, 14),
        ),
    ]
    fake_email = FakeEmailClient()
    service = ExpirationEmailReminderService(repository=repository, email_client=fake_email)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    sent = fake_email.sent_messages[0]
    assert "以下是 2026-05-14 即將到期的食材：" in sent.content_text
    assert "胡蘿蔔 | 1 | 份 | 冰箱" in sent.content_text
    assert "番茄 | 1.5 | 份 | 冰箱" in sent.content_text
    assert "胡蘿蔔 | 1.0" not in sent.content_text
    assert "番茄 | 1.50" not in sent.content_text
    assert sent.content_text.endswith(EXPECTED_FOOTER)


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

    assert result.failed_count == 2
    assert result.retry_count == 1
    assert result.permanent_failed_count == 1
    assert repository.deliveries[0].status == "failed"
    assert repository.deliveries[0].final_status == "permanent_failed"
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


def test_morning_should_cleanup_logs_older_than_7_days() -> None:
    """morning_08 應清除超過 7 天紀錄。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 5),
            send_window="morning_08",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        ),
        FakeDelivery(
            id=2,
            user_id=1,
            scheduled_date=date(2026, 5, 6),
            send_window="evening_17",
            reminder_days="1",
            item_ids=[2],
            email_to="u1@example.com",
            status="success",
        ),
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert repository.cleanup_cutoff_dates == [date(2026, 5, 6)]
    assert [row.id for row in repository.deliveries] == [2]


def test_morning_should_not_cleanup_logs_within_7_days() -> None:
    """morning_08 不應刪除 7 天內紀錄。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 6),
            send_window="morning_08",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        ),
        FakeDelivery(
            id=2,
            user_id=1,
            scheduled_date=date(2026, 5, 7),
            send_window="evening_17",
            reminder_days="1",
            item_ids=[2],
            email_to="u1@example.com",
            status="success",
        ),
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert repository.cleanup_cutoff_dates == [date(2026, 5, 6)]
    assert [row.id for row in repository.deliveries] == [1, 2]


def test_evening_should_not_run_cleanup() -> None:
    """evening_17 不應執行 cleanup。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 1),
            send_window="morning_08",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        )
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="evening_17")

    assert repository.cleanup_cutoff_dates == []
    assert [row.id for row in repository.deliveries] == [1]


def test_cleanup_should_not_affect_today_new_delivery() -> None:
    """cleanup 不應影響當天新產生寄送紀錄。"""
    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=101, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    repository.deliveries = [
        FakeDelivery(
            id=1,
            user_id=1,
            scheduled_date=date(2026, 5, 1),
            send_window="morning_08",
            reminder_days="1",
            item_ids=[1],
            email_to="u1@example.com",
            status="success",
        )
    ]
    service = ExpirationEmailReminderService(repository=repository, email_client=FakeEmailClient())

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.success_count == 1
    assert len(repository.deliveries) == 1
    assert repository.deliveries[0].scheduled_date == date(2026, 5, 13)


def test_gmail_smtp_failed_result_should_be_recorded_to_delivery_log(monkeypatch) -> None:
    """SMTP 失敗時 service 應將 delivery log 寫為 failed。"""
    class FailingSmtp:
        """測試用失敗 SMTP。"""

        def __init__(self, host: str, port: int, timeout: int):
            self.host = host
            self.port = port
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self) -> None:
            """模擬 EHLO。"""

        def starttls(self) -> None:
            """模擬 STARTTLS。"""

        def login(self, username: str, password: str) -> None:
            """模擬 login。"""

        def send_message(self, message) -> None:
            """模擬寄送失敗。"""
            raise RuntimeError("smtp down")

    monkeypatch.setattr("backend.app.infra.email_client.smtplib.SMTP", FailingSmtp)

    repository = FakeExpirationEmailReminderRepository()
    repository.users = [(FakeUser(id=1, email="u1@example.com", display_name="小明"), FakePreference(expiration_email_reminder_days="1"))]
    repository.items = [FakePantryItem(id=1, user_id=1, name="牛奶", expiration_date=date(2026, 5, 14))]
    email_client = GmailSmtpEmailClient(
        host="smtp.gmail.com",
        port=587,
        username="dev@gmail.com",
        app_password="app-password",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )
    service = ExpirationEmailReminderService(repository=repository, email_client=email_client)

    result = service.run_for_window(scheduled_date=date(2026, 5, 13), send_window="morning_08")

    assert result.failed_count == 2
    assert result.retry_count == 1
    assert result.permanent_failed_count == 1
    assert repository.deliveries[0].status == "failed"
    assert repository.deliveries[0].final_status == "permanent_failed"
    assert repository.deliveries[0].error_message is not None
