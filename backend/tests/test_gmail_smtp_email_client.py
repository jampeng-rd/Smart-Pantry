"""Gmail SMTP Email client 測試。"""

from __future__ import annotations

from backend.app.infra.email_client import EmailMessage, GmailSmtpEmailClient


class FakeSmtpServer:
    """測試用 SMTP 伺服器。"""

    last_instance: "FakeSmtpServer | None" = None

    def __init__(self, host: str, port: int, timeout: int):
        """建立測試 SMTP 實例。"""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.login_username = ""
        self.login_password = ""
        self.sent_message = None
        FakeSmtpServer.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self) -> None:
        """模擬 EHLO。"""

    def starttls(self) -> None:
        """模擬 STARTTLS。"""
        self.started_tls = True

    def login(self, username: str, password: str) -> None:
        """模擬 SMTP login。"""
        self.login_username = username
        self.login_password = password

    def send_message(self, message) -> None:
        """記錄發送訊息。"""
        self.sent_message = message


class FakeFailingSmtpServer(FakeSmtpServer):
    """測試用失敗 SMTP 伺服器。"""

    def send_message(self, message) -> None:
        """模擬寄送失敗。"""
        raise RuntimeError("smtp failure with secret app-password")


def test_gmail_smtp_client_should_send_email_successfully(monkeypatch) -> None:
    """SMTP 成功時應有正確 subject/to/from/body。"""
    monkeypatch.setattr("backend.app.infra.email_client.smtplib.SMTP", FakeSmtpServer)

    client = GmailSmtpEmailClient(
        host="smtp.gmail.com",
        port=587,
        username="dev@gmail.com",
        app_password="app-password",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )

    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="提醒測試",
            content_text="這是一封測試信",
        )
    )

    assert result.success is True
    sent = FakeSmtpServer.last_instance
    assert sent is not None
    assert sent.host == "smtp.gmail.com"
    assert sent.port == 587
    assert sent.timeout == 30
    assert sent.started_tls is True
    assert sent.login_username == "dev@gmail.com"
    assert sent.login_password == "app-password"
    assert sent.sent_message["Subject"] == "提醒測試"
    assert sent.sent_message["To"] == "user@example.com"
    assert sent.sent_message["From"] == "Smart Pantry <no-reply@example.com>"
    assert "這是一封測試信" in sent.sent_message.get_content()


def test_gmail_smtp_client_should_send_multipart_when_html_exists(monkeypatch) -> None:
    """有 content_html 時應寄 multipart/alternative，含 text/plain 與 text/html。"""
    monkeypatch.setattr("backend.app.infra.email_client.smtplib.SMTP", FakeSmtpServer)

    client = GmailSmtpEmailClient(
        host="smtp.gmail.com",
        port=587,
        username="dev@gmail.com",
        app_password="app-password",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )

    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="提醒測試",
            content_text="純文字內容",
            content_html="<html><body><p>HTML 內容</p></body></html>",
        )
    )

    assert result.success is True
    sent = FakeSmtpServer.last_instance
    assert sent is not None
    message = sent.sent_message
    assert message.is_multipart() is True
    plain_part = message.get_body(preferencelist=("plain",))
    html_part = message.get_body(preferencelist=("html",))
    assert plain_part is not None
    assert html_part is not None
    assert "純文字內容" in plain_part.get_content()
    assert "HTML 內容" in html_part.get_content()


def test_gmail_smtp_client_should_fail_without_leaking_password(monkeypatch) -> None:
    """SMTP 失敗時不應洩漏密碼，且回友善錯誤。"""
    monkeypatch.setattr("backend.app.infra.email_client.smtplib.SMTP", FakeFailingSmtpServer)

    client = GmailSmtpEmailClient(
        host="smtp.gmail.com",
        port=587,
        username="dev@gmail.com",
        app_password="app-password",
        from_name="Smart Pantry",
        from_address="no-reply@example.com",
    )

    result = client.send_email(
        EmailMessage(
            to_email="user@example.com",
            subject="提醒測試",
            content_text="這是一封測試信",
        )
    )

    assert result.success is False
    assert result.error_message is not None
    assert "寄送失敗" in result.error_message
    assert "app-password" not in result.error_message
