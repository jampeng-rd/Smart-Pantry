"""Resend Email client 實作。"""

from __future__ import annotations

import json
import logging
import socket
from urllib import error, request

from backend.app.infra.email_client import BaseEmailClient, EmailMessage, EmailSendResult

LOGGER = logging.getLogger(__name__)


class ResendEmailClient(BaseEmailClient):
    """使用 Resend HTTP API 寄送信件，支援 text/html。"""

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
        url = f"{self.api_base_url}/emails"
        payload = {
            "from": f"{self.from_name} <{self.from_address}>",
            "to": [message.to_email],
            "subject": message.subject,
            "text": message.content_text,
        }
        if message.content_html:
            payload["html"] = message.content_html
        body = json.dumps(payload).encode("utf-8")
        request_obj = request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Smart Pantry Backend/1.0",
            },
        )

        try:
            LOGGER.info(
                "resend send start api_base_url=%s from_address=%s to_email=%s subject=%s",
                self.api_base_url,
                self.from_address,
                message.to_email,
                message.subject,
            )
            with request.urlopen(request_obj, timeout=30) as response:
                status_code = getattr(response, "status", None)
                if status_code is None or 200 <= status_code < 300:
                    LOGGER.info(
                        "resend send success api_base_url=%s from_address=%s to_email=%s subject=%s status_code=%s",
                        self.api_base_url,
                        self.from_address,
                        message.to_email,
                        message.subject,
                        status_code,
                    )
                    return EmailSendResult(success=True, should_retry=False, error_category=None, error_message=None)
                LOGGER.error(
                    "resend send unexpected status api_base_url=%s from_address=%s to_email=%s subject=%s status_code=%s",
                    self.api_base_url,
                    self.from_address,
                    message.to_email,
                    message.subject,
                    status_code,
                )
                return EmailSendResult(
                    success=False,
                    should_retry=False,
                    error_category="unknown_error",
                    error_message="Resend 寄送失敗，請稍後再試",
                )
        except error.HTTPError as exc:
            response_body = ""
            if exc.fp is not None:
                response_body = exc.fp.read().decode("utf-8", errors="replace")
            response_summary = self._summarize_error_body(response_body=response_body)
            LOGGER.error(
                "resend send http error api_base_url=%s from_address=%s to_email=%s subject=%s status_code=%s summary=%s",
                self.api_base_url,
                self.from_address,
                message.to_email,
                message.subject,
                exc.code,
                response_summary,
            )
            error_category = "provider_5xx" if 500 <= exc.code < 600 else "provider_4xx"
            if exc.code < 500 and self._is_invalid_configuration_error(response_summary):
                error_category = "invalid_configuration"
            return EmailSendResult(
                success=False,
                should_retry=500 <= exc.code < 600,
                error_category=error_category,
                error_message=f"Resend 寄送失敗（HTTP {exc.code}）：{response_summary}",
            )
        except TimeoutError as exc:
            safe_summary = self._sanitize_error_text(str(exc)) or "請求逾時"
            return EmailSendResult(
                success=False,
                should_retry=True,
                error_category="timeout",
                error_message=f"Resend 寄送失敗（TimeoutError）：{safe_summary}",
            )
        except socket.timeout as exc:
            safe_summary = self._sanitize_error_text(str(exc)) or "請求逾時"
            return EmailSendResult(
                success=False,
                should_retry=True,
                error_category="timeout",
                error_message=f"Resend 寄送失敗（timeout）：{safe_summary}",
            )
        except error.URLError as exc:
            safe_summary = self._sanitize_error_text(str(exc.reason)) or "網路錯誤"
            return EmailSendResult(
                success=False,
                should_retry=True,
                error_category="network_error",
                error_message=f"Resend 寄送失敗（URLError）：{safe_summary}",
            )
        except Exception as exc:
            safe_summary = self._sanitize_error_text(str(exc)) or "未知錯誤"
            exception_type = exc.__class__.__name__
            LOGGER.error(
                "resend send exception api_base_url=%s from_address=%s to_email=%s subject=%s exception_type=%s summary=%s",
                self.api_base_url,
                self.from_address,
                message.to_email,
                message.subject,
                exception_type,
                safe_summary,
            )
            return EmailSendResult(
                success=False,
                should_retry=False,
                error_category="unknown_error",
                error_message=f"Resend 寄送失敗（{exception_type}）：{safe_summary}",
            )

    def _summarize_error_body(self, response_body: str) -> str:
        """解析 Resend 錯誤回應摘要，避免洩漏敏感資訊。"""
        body = response_body.strip()
        if not body:
            return "無回應內容"

        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                for key in ("message", "error", "name"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        return self._sanitize_error_text(value.strip()) or "無法解析錯誤摘要"
            return "JSON 錯誤回應格式不符預期"
        except json.JSONDecodeError:
            text = self._sanitize_error_text(body)
            if text:
                return f"非 JSON 回應：{text[:200]}"
            return "非 JSON 回應（內容已隱藏）"

    def _sanitize_error_text(self, text: str) -> str:
        """移除可能包含 secret 的片段，保留可除錯摘要。"""
        safe_text = text.replace(self.api_key, "[REDACTED]")
        return safe_text

    def _is_invalid_configuration_error(self, summary: str) -> bool:
        """判斷是否屬於不可重試的設定類錯誤。"""
        lowered = summary.lower()
        keywords = [
            "verified domain",
            "from address",
            "invalid recipient",
            "invalid sender",
            "domain",
            "configuration",
        ]
        return any(keyword in lowered for keyword in keywords)
