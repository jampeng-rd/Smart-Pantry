"""Email client 抽象層與 fake 實作。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """單封 Email 要寄送的內容。"""

    to_email: str
    subject: str
    content_text: str


@dataclass
class EmailSendResult:
    """Email 寄送結果。"""

    success: bool
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
            return EmailSendResult(success=False, error_message="FakeEmailClient 模擬寄送失敗")
        return EmailSendResult(success=True, error_message=None)
