"""Resend Email client 實作。"""

from __future__ import annotations

import json
from urllib import error, request

from backend.app.infra.email_client import BaseEmailClient, EmailMessage, EmailSendResult


class ResendEmailClient(BaseEmailClient):
    """使用 Resend HTTP API 寄送純文字信件。"""

    def __init__(
        self,
        api_key: str,
        from_name: str,
        from_address: str,
        api_base_url: str = "https://api.resend.com",
    ):
        """建立 Resend client。"""
        self.api_key = api_key
        self.from_name = from_name
        self.from_address = from_address
        self.api_base_url = api_base_url.rstrip("/")

    def send_email(self, message: EmailMessage) -> EmailSendResult:
        """呼叫 Resend API 寄信，失敗時回傳不含 secret 的友善訊息。"""
        payload = {
            "from": f"{self.from_name} <{self.from_address}>",
            "to": [message.to_email],
            "subject": message.subject,
            "text": message.content_text,
        }
        body = json.dumps(payload).encode("utf-8")
        request_obj = request.Request(
            url=f"{self.api_base_url}/emails",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(request_obj, timeout=30) as response:
                status_code = getattr(response, "status", None)
                if status_code is None or 200 <= status_code < 300:
                    return EmailSendResult(success=True, error_message=None)
                return EmailSendResult(success=False, error_message="Resend 寄送失敗，請稍後再試")
        except error.HTTPError as exc:
            if 400 <= exc.code < 500:
                return EmailSendResult(success=False, error_message="Resend 寄送失敗，請檢查寄件者網域或收件資訊")
            return EmailSendResult(success=False, error_message="Resend 服務暫時無法使用，請稍後再試")
        except Exception:
            return EmailSendResult(success=False, error_message="Resend 寄送失敗，請檢查網路連線後再試")
