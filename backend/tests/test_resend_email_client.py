"""Resend Email client 測試。"""

from __future__ import annotations

import io
from urllib import error

from backend.app.infra.email_client import EmailMessage
from backend.app.infra.resend_email_client import ResendEmailClient


class FakeHttpResponse:
    """測試用 HTTP 成功回應。"""

    def __init__(self, status: int):
        """建立假回應。"""
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_resend_client_should_send_expected_payload(monkeypatch) -> None:
    """成功時應送出正確 payload 與 header。"""
    captured = {}

    def fake_urlopen(request_obj, timeout: int):
        captured["url"] = request_obj.full_url
        captured["timeout"] = timeout
        captured["authorization"] = request_obj.headers.get("Authorization")
        captured["content_type"] = request_obj.headers.get("Content-type")
        captured["user_agent"] = request_obj.headers.get("User-agent")
        captured["body"] = request_obj.data.decode("utf-8")
        return FakeHttpResponse(status=200)

    monkeypatch.setattr("backend.app.infra.resend_email_client.request.urlopen", fake_urlopen)

    client = ResendEmailClient(
        api_key="re_test_secret_key",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
        api_base_url="https://api.resend.com",
    )
    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="到期提醒",
            content_text="牛奶將於明天到期",
        )
    )

    assert result.success is True
    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["timeout"] == 30
    assert captured["authorization"] == "Bearer re_test_secret_key"
    assert captured["content_type"] == "application/json"
    assert captured["user_agent"] == "Smart Pantry Backend/1.0"
    assert '"from": "Smart Pantry <no-reply@example.com>"' in captured["body"]
    assert '"to": ["user@example.com"]' in captured["body"]
    assert '"subject": "\\u5230\\u671f\\u63d0\\u9192"' in captured["body"]
    assert '"text": "\\u725b\\u5976\\u5c07\\u65bc\\u660e\\u5929\\u5230\\u671f"' in captured["body"]


def test_resend_client_should_fail_without_leaking_api_key(monkeypatch, caplog) -> None:
    """失敗時應回 failed 且錯誤訊息不得含 API key。"""

    def fake_urlopen(_request_obj, _timeout: int):
        raise RuntimeError("network failed: re_test_secret_key")

    monkeypatch.setattr("backend.app.infra.resend_email_client.request.urlopen", fake_urlopen)

    client = ResendEmailClient(
        api_key="re_test_secret_key",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )
    with caplog.at_level("ERROR"):
        result = client.send_email(
            EmailMessage(
                to_email="user@example.com",
                subject="到期提醒",
                content_text="牛奶將於明天到期",
            )
        )

    assert result.success is False
    assert result.error_message is not None
    assert "re_test_secret_key" not in result.error_message
    assert "Authorization" not in caplog.text
    assert "Bearer " not in caplog.text
    assert "re_test_secret_key" not in caplog.text


def test_resend_client_should_return_friendly_message_for_http_client_error(monkeypatch) -> None:
    """HTTPError JSON message 應回傳到 error_message 供 delivery log 記錄。"""

    def fake_urlopen(_request_obj, timeout: int):
        raise error.HTTPError(
            url="https://api.resend.com/emails",
            code=403,
            msg="forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"message":"The from address does not match your verified domain."}'),
        )

    monkeypatch.setattr("backend.app.infra.resend_email_client.request.urlopen", fake_urlopen)

    client = ResendEmailClient(
        api_key="re_test_secret_key",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )
    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="到期提醒",
            content_text="牛奶將於明天到期",
        )
    )

    assert result.success is False
    assert result.error_message is not None
    assert "HTTP 403" in result.error_message
    assert "verified domain" in result.error_message
    assert "re_test_secret_key" not in result.error_message


def test_resend_client_should_return_http_status_and_non_json_summary(monkeypatch) -> None:
    """HTTPError 非 JSON body 時，應帶 HTTP status 與安全摘要。"""

    def fake_urlopen(_request_obj, timeout: int):
        raise error.HTTPError(
            url="https://api.resend.com/emails",
            code=422,
            msg="unprocessable",
            hdrs=None,
            fp=io.BytesIO(b"bad request with secret re_test_secret_key"),
        )

    monkeypatch.setattr("backend.app.infra.resend_email_client.request.urlopen", fake_urlopen)

    client = ResendEmailClient(
        api_key="re_test_secret_key",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )
    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="到期提醒",
            content_text="牛奶將於明天到期",
        )
    )

    assert result.success is False
    assert result.error_message is not None
    assert "HTTP 422" in result.error_message
    assert "非 JSON 回應" in result.error_message
    assert "re_test_secret_key" not in result.error_message
