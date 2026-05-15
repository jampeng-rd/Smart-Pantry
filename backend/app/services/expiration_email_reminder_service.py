"""到期 Email 提醒商業邏輯服務。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import logging
import time

from backend.app.infra.email_client import BaseEmailClient, EmailMessage
from backend.app.infra.repository.expiration_email_reminder_repository import ExpirationEmailReminderRepository

VALID_SEND_WINDOWS = {"morning_08", "evening_17"}
VALID_REMINDER_DAYS = {"none", "1", "3"}
RETRY_BACKOFF_SECONDS = [5, 15, 30]
LOGGER = logging.getLogger(__name__)


@dataclass
class ExpirationReminderRunResult:
    """單次提醒排程執行摘要。"""

    scheduled_date: date
    send_window: str
    total_users: int
    skipped_none: int
    skipped_duplicate: int
    skipped_no_items: int
    success_count: int
    failed_count: int
    retry_count: int
    permanent_failed_count: int


class ExpirationEmailReminderService:
    """依使用者偏好寄送到期提醒，並記錄 delivery log。"""
    FOOTER_TEXT = "此信件由系統自動發送，無需回覆。"

    def __init__(
        self,
        repository: ExpirationEmailReminderRepository,
        email_client: BaseEmailClient,
        retry_max_attempts: int = 1,
        sleep_fn=time.sleep,
    ):
        """建立提醒服務實例。"""
        self.repository = repository
        self.email_client = email_client
        self.retry_max_attempts = max(0, min(3, retry_max_attempts))
        self.sleep_fn = sleep_fn

    def run_for_window(self, scheduled_date: date, send_window: str) -> ExpirationReminderRunResult:
        """執行指定日期與時段的到期提醒流程。"""
        if send_window not in VALID_SEND_WINDOWS:
            raise ValueError("不支援的 send_window")

        # 每日僅在 morning_08 清理一次超過 7 天的寄送紀錄，避免重複清理。
        if send_window == "morning_08":
            cutoff_date = scheduled_date - timedelta(days=7)
            self.repository.delete_old_deliveries_before(cutoff_scheduled_date=cutoff_date)

        users_with_preferences = self.repository.list_users_with_preferences()

        result = ExpirationReminderRunResult(
            scheduled_date=scheduled_date,
            send_window=send_window,
            total_users=len(users_with_preferences),
            skipped_none=0,
            skipped_duplicate=0,
            skipped_no_items=0,
            success_count=0,
            failed_count=0,
            retry_count=0,
            permanent_failed_count=0,
        )

        for user, preference in users_with_preferences:
            reminder_days = self._resolve_reminder_days(preference.expiration_email_reminder_days if preference else None)
            if reminder_days == "none":
                result.skipped_none += 1
                continue

            if self.repository.has_success_delivery(user_id=user.id, scheduled_date=scheduled_date, send_window=send_window):
                result.skipped_duplicate += 1
                continue

            target_date = self._get_target_expiration_date(scheduled_date=scheduled_date, reminder_days=reminder_days)
            pantry_items = self.repository.list_items_by_user_and_expiration_date(user_id=user.id, expiration_date=target_date)
            if not pantry_items:
                result.skipped_no_items += 1
                continue

            delivery = self.repository.create_delivery(
                user_id=user.id,
                scheduled_date=scheduled_date,
                send_window=send_window,
                reminder_days=reminder_days,
                item_ids=[item.id for item in pantry_items],
                email_to=user.email,
            )

            message = self._build_email_message(
                display_name=user.display_name,
                email_to=user.email,
                target_expiration_date=target_date,
                pantry_items=pantry_items,
            )
            self._send_with_retry(
                delivery=delivery,
                message=message,
                result=result,
                user_id=user.id,
                scheduled_date=scheduled_date,
                send_window=send_window,
            )

        return result

    def _send_with_retry(self, delivery, message: EmailMessage, result: ExpirationReminderRunResult, user_id: int, scheduled_date: date, send_window: str) -> None:
        """處理單次寄送與重試邏輯。"""
        total_attempts = 1 + self.retry_max_attempts
        attempt = 0
        while attempt < total_attempts:
            attempt += 1
            attempted_at = datetime.now(timezone.utc)
            email_result = self.email_client.send_email(message)

            if email_result.success:
                self.repository.mark_delivery_success(row=delivery, sent_at=attempted_at, attempt_count=attempt)
                result.success_count += 1
                return

            safe_error_message = email_result.error_message or "寄送失敗"
            can_retry = bool(email_result.should_retry and attempt <= self.retry_max_attempts)
            if can_retry:
                self.repository.mark_delivery_failed(
                    row=delivery,
                    error_message=safe_error_message,
                    error_category=email_result.error_category,
                    attempt_count=attempt,
                    attempted_at=attempted_at,
                    permanent=False,
                )
                result.failed_count += 1
                result.retry_count += 1
                LOGGER.warning(
                    "email temporary failure user_id=%s scheduled_date=%s send_window=%s attempt=%s category=%s should_retry=true",
                    user_id,
                    scheduled_date.isoformat(),
                    send_window,
                    attempt,
                    email_result.error_category,
                )
                LOGGER.info(
                    "email send retry user_id=%s scheduled_date=%s send_window=%s next_attempt=%s backoff_seconds=%s",
                    user_id,
                    scheduled_date.isoformat(),
                    send_window,
                    attempt + 1,
                    self._retry_backoff_seconds(attempt),
                )
                self.sleep_fn(self._retry_backoff_seconds(attempt))
                continue

            self.repository.mark_delivery_failed(
                row=delivery,
                error_message=safe_error_message,
                error_category=email_result.error_category,
                attempt_count=attempt,
                attempted_at=attempted_at,
                permanent=True,
            )
            result.failed_count += 1
            result.permanent_failed_count += 1
            LOGGER.error(
                "email permanent failure user_id=%s scheduled_date=%s send_window=%s attempt=%s category=%s should_retry=%s",
                user_id,
                scheduled_date.isoformat(),
                send_window,
                attempt,
                email_result.error_category,
                email_result.should_retry,
            )
            return

    def _retry_backoff_seconds(self, attempt_index: int) -> int:
        """依重試次數回傳固定 backoff 秒數。"""
        if attempt_index <= 0:
            return RETRY_BACKOFF_SECONDS[0]
        if attempt_index > len(RETRY_BACKOFF_SECONDS):
            return RETRY_BACKOFF_SECONDS[-1]
        return RETRY_BACKOFF_SECONDS[attempt_index - 1]

    def _resolve_reminder_days(self, raw_value: str | None) -> str:
        """解析提醒天數，不合法值 fallback 為 1 天。"""
        if raw_value in VALID_REMINDER_DAYS:
            return raw_value
        return "1"

    def _get_target_expiration_date(self, scheduled_date: date, reminder_days: str) -> date:
        """依提醒天數計算本次應提醒的到期日。"""
        if reminder_days == "1":
            return scheduled_date + timedelta(days=1)
        if reminder_days == "3":
            return scheduled_date + timedelta(days=3)
        raise ValueError("none 不應進入到期日計算")

    def _build_email_message(
        self,
        display_name: str,
        email_to: str,
        target_expiration_date: date,
        pantry_items: list,
    ) -> EmailMessage:
        """建立提醒信內容（純文字 + HTML）。"""
        text_item_lines = "\n".join([
            (
                f"{item.name} | {self._format_quantity(item.quantity)} | {item.unit} | "
                f"{self._format_storage_location(item.storage_location)}"
            )
            for item in pantry_items
        ])
        text_content = (
            f"{display_name} 您好：\n\n"
            f"以下是 {target_expiration_date.isoformat()} 即將到期的食材：\n\n"
            "食材名稱 | 數量 | 單位 | 保存位置\n"
            f"{text_item_lines}\n\n"
            f"{self.FOOTER_TEXT}"
        )
        html_table_rows = "".join([
            (
                "<tr>"
                f"<td style=\"padding:8px;border:1px solid #d1d5db;\">{self._escape_html(item.name)}</td>"
                f"<td style=\"padding:8px;border:1px solid #d1d5db;\">{self._escape_html(self._format_quantity(item.quantity))}</td>"
                f"<td style=\"padding:8px;border:1px solid #d1d5db;\">{self._escape_html(item.unit)}</td>"
                f"<td style=\"padding:8px;border:1px solid #d1d5db;\">{self._escape_html(self._format_storage_location(item.storage_location))}</td>"
                "</tr>"
            )
            for item in pantry_items
        ])
        html_content = (
            "<div style=\"font-family:Arial,'Noto Sans TC',sans-serif;color:#1f2937;line-height:1.6;\">"
            "<h2 style=\"margin:0 0 12px 0;font-size:22px;\">食材即將到期提醒</h2>"
            f"<p style=\"margin:0 0 10px 0;\">{self._escape_html(display_name)} 您好：</p>"
            f"<p style=\"margin:0 0 14px 0;\">以下是 {target_expiration_date.isoformat()} 即將到期的食材：</p>"
            "<table style=\"border-collapse:collapse;width:100%;\">"
            "<thead><tr>"
            "<th style=\"text-align:left;padding:8px;border:1px solid #d1d5db;background:#f3f4f6;\">食材名稱</th>"
            "<th style=\"text-align:left;padding:8px;border:1px solid #d1d5db;background:#f3f4f6;\">數量</th>"
            "<th style=\"text-align:left;padding:8px;border:1px solid #d1d5db;background:#f3f4f6;\">單位</th>"
            "<th style=\"text-align:left;padding:8px;border:1px solid #d1d5db;background:#f3f4f6;\">保存位置</th>"
            "</tr></thead>"
            f"<tbody>{html_table_rows}</tbody>"
            "</table>"
            f"<p style=\"margin:14px 0 0 0;\">{self._escape_html(self.FOOTER_TEXT)}</p>"
            "</div>"
        )
        return EmailMessage(
            to_email=email_to,
            subject="【智慧食材保存系統】食材到期提醒",
            content_text=text_content,
            content_html=html_content,
        )

    def _format_storage_location(self, storage_location: str | None) -> str:
        """格式化保存位置，空值顯示未設定。"""
        if storage_location is None:
            return "未設定"
        cleaned = storage_location.strip()
        if not cleaned:
            return "未設定"
        return cleaned

    def _format_quantity(self, quantity: int | float) -> str:
        """格式化數量：整數不顯示小數，非整數保留必要小數。"""
        value = float(quantity)
        if value.is_integer():
            return str(int(value))
        return f"{value:g}"

    def _escape_html(self, text: str) -> str:
        """簡易 HTML escaping，避免內容破壞版型。"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )
