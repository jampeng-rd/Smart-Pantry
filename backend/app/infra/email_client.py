"""Email client 抽象層與 fake 實作。"""

from __future__ import annotations

import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.message import EmailMessage as SmtpEmailMessage
from typing import Literal

EmailErrorCategory = Literal[
    "timeout",
    "network_error",
    "provider_4xx",
    "provider_5xx",
    "invalid_configuration",
    "unknown_error",
]


@dataclass
class EmailMessage:
    """單封 Email 要寄送的內容。"""

    to_email: str
    subject: str
    content_text: str
    content_html: str | None = None


@dataclass
class EmailSendResult:
    """Email 寄送結果。"""

    success: bool
    should_retry: bool = False
    error_category: EmailErrorCategory | None = None
    error_message: str | None = None


class BaseEmailClient(ABC):
    """Email client 抽象介面，service 僅依賴此介面。"""

    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailSendResult:
        """送出 Email，回傳成功或失敗結果。"""


class FakeEmailClient(BaseEmailClient):
    """測試與開發用假 Email client。"""

    def __init__(self, force_fail: bool = False, fail_targets: set[str] | None = None):
        """建立 fake client，支援全域或指定收件者失敗。"""
        self.force_fail = force_fail
        self.fail_targets = fail_targets or set()
        self.sent_messages: list[EmailMessage] = []

    def send_email(self, message: EmailMessage) -> EmailSendResult:
        """記錄內容並回傳假成功/失敗結果。"""
        self.sent_messages.append(message)
        if self.force_fail or message.to_email in self.fail_targets:
            return EmailSendResult(
                success=False,
                should_retry=True,
                error_category="network_error",
                error_message="FakeEmailClient 模擬寄送失敗",
            )
        return EmailSendResult(success=True, error_message=None)


class GmailSmtpEmailClient(BaseEmailClient):
    """使用 Gmail SMTP（STARTTLS）寄送信件，支援 text/html。"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        app_password: str,
        from_name: str,
        from_address: str,
    ):
        """建立 Gmail SMTP client。"""
        self.host = host
        self.port = port
        self.username = username
        self.app_password = app_password
        self.from_name = from_name
        self.from_address = from_address

    def send_email(self, message: EmailMessage) -> EmailSendResult:
        """透過 SMTP 寄信，成功回 success，失敗回安全錯誤訊息。"""
        smtp_message = SmtpEmailMessage()
        smtp_message["Subject"] = message.subject
        smtp_message["To"] = message.to_email
        smtp_message["From"] = f"{self.from_name} <{self.from_address}>"
        smtp_message.set_content(message.content_text)
        if message.content_html:
            smtp_message.add_alternative(message.content_html, subtype="html")

        try:
            with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.username, self.app_password)
                smtp.send_message(smtp_message)
        except Exception:
            return EmailSendResult(
                success=False,
                should_retry=True,
                error_category="network_error",
                error_message="Gmail SMTP 寄送失敗，請檢查帳號、App Password 或網路連線",
            )

        return EmailSendResult(success=True, error_message=None)
