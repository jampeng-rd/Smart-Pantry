"""到期 Email 提醒商業邏輯服務。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from backend.app.infra.email_client import BaseEmailClient, EmailMessage
from backend.app.infra.repository.expiration_email_reminder_repository import ExpirationEmailReminderRepository

VALID_SEND_WINDOWS = {"morning_08", "evening_17"}
VALID_REMINDER_DAYS = {"none", "1", "3"}


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


class ExpirationEmailReminderService:
    """依使用者偏好寄送到期提醒，並記錄 delivery log。"""

    def __init__(self, repository: ExpirationEmailReminderRepository, email_client: BaseEmailClient):
        """建立提醒服務實例。"""
        self.repository = repository
        self.email_client = email_client

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
            email_result = self.email_client.send_email(message)
            if email_result.success:
                self.repository.mark_delivery_success(row=delivery, sent_at=datetime.now(timezone.utc))
                result.success_count += 1
            else:
                self.repository.mark_delivery_failed(row=delivery, error_message=email_result.error_message or "寄送失敗")
                result.failed_count += 1

        return result

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
        """建立純文字提醒信內容。"""
        item_lines = "\n".join([
            (
                f"{item.name} | {self._format_quantity(item.quantity)} | {item.unit} | "
                f"{self._format_storage_location(item.storage_location)}"
            )
            for item in pantry_items
        ])
        content = (
            f"{display_name} 您好：\n\n"
            f"以下是 {target_expiration_date.isoformat()} 即將到期的食材：\n\n"
            "食材名稱 | 數量 | 單位 | 保存位置\n"
            f"{item_lines}\n\n"
            "此信件來自【智慧食材保存與膳食管理系統】自動發送\n"
            "無需回信 謝謝您。\n\n"
        )
        return EmailMessage(
            to_email=email_to,
            subject="【智慧食材保存系統】食材即將到期提醒",
            content_text=content,
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
