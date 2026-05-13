"""Email provider settings 與 factory 測試。"""

from __future__ import annotations

import pytest

from backend.app.infra.email_client import FakeEmailClient, GmailSmtpEmailClient
from backend.app.infra.email_client_factory import build_email_client
from backend.app.infra.settings import Settings


def test_settings_should_read_email_provider_fake() -> None:
    """Settings 應可讀取 EMAIL_PROVIDER=fake。"""
    settings = Settings(email_provider="fake")
    assert settings.email_provider == "fake"


def test_settings_should_read_email_provider_gmail_smtp() -> None:
    """Settings 應可讀取 EMAIL_PROVIDER=gmail_smtp。"""
    settings = Settings(email_provider="gmail_smtp")
    assert settings.email_provider == "gmail_smtp"


def test_settings_should_accept_email_provider_related_fields() -> None:
    """含 Email Provider 欄位時，Settings 不應出現 extra forbidden 錯誤。"""
    settings = Settings(
        email_provider="gmail_smtp",
        email_from_name="Smart Pantry",
        email_from_address="",
        gmail_smtp_host="smtp.gmail.com",
        gmail_smtp_port=587,
        gmail_smtp_username="dev@example.com",
        gmail_smtp_app_password="app-password",
        production_email_provider="resend",
        resend_api_key="",
        sendgrid_api_key="",
        aws_ses_region="",
        aws_ses_access_key_id="",
        aws_ses_secret_access_key="",
    )
    assert settings.gmail_smtp_host == "smtp.gmail.com"


def test_settings_should_not_fail_with_email_provider_env_fields(monkeypatch) -> None:
    """使用 env 注入 Email Provider 欄位時，不應觸發 extra forbidden。"""
    monkeypatch.setenv("EMAIL_PROVIDER", "fake")
    monkeypatch.setenv("EMAIL_FROM_NAME", "Smart Pantry")
    monkeypatch.setenv("EMAIL_FROM_ADDRESS", "no-reply@example.com")
    monkeypatch.setenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("GMAIL_SMTP_PORT", "587")
    monkeypatch.setenv("GMAIL_SMTP_USERNAME", "")
    monkeypatch.setenv("GMAIL_SMTP_APP_PASSWORD", "")
    monkeypatch.setenv("PRODUCTION_EMAIL_PROVIDER", "resend")
    monkeypatch.setenv("RESEND_API_KEY", "")
    monkeypatch.setenv("SENDGRID_API_KEY", "")
    monkeypatch.setenv("AWS_SES_REGION", "")
    monkeypatch.setenv("AWS_SES_ACCESS_KEY_ID", "")
    monkeypatch.setenv("AWS_SES_SECRET_ACCESS_KEY", "")

    settings = Settings()

    assert settings.email_provider == "fake"


def test_factory_should_return_fake_client_when_email_provider_fake() -> None:
    """EMAIL_PROVIDER=fake 時，factory 應回 FakeEmailClient。"""
    settings = Settings(email_provider="fake")
    client = build_email_client(settings)
    assert isinstance(client, FakeEmailClient)


def test_factory_should_return_gmail_client_when_email_provider_gmail_smtp() -> None:
    """EMAIL_PROVIDER=gmail_smtp 時，factory 應回 GmailSmtpEmailClient。"""
    settings = Settings(
        email_provider="gmail_smtp",
        email_from_name="Smart Pantry",
        email_from_address="",
        gmail_smtp_host="smtp.gmail.com",
        gmail_smtp_port=587,
        gmail_smtp_username="dev@example.com",
        gmail_smtp_app_password="app-password",
    )
    client = build_email_client(settings)
    assert isinstance(client, GmailSmtpEmailClient)
    assert client.from_address == "dev@example.com"


def test_factory_should_fail_with_friendly_error_when_gmail_credentials_missing() -> None:
    """gmail_smtp 模式缺少帳密時應回中文友善錯誤。"""
    settings = Settings(email_provider="gmail_smtp", gmail_smtp_username="", gmail_smtp_app_password="")

    with pytest.raises(ValueError) as exc:
        build_email_client(settings)

    assert "gmail_smtp 模式需要設定" in str(exc.value)


def test_factory_should_raise_not_implemented_for_production_provider() -> None:
    """production 模式本階段應回尚未實作錯誤。"""
    settings = Settings(email_provider="production")

    with pytest.raises(NotImplementedError) as exc:
        build_email_client(settings)

    assert "尚未實作" in str(exc.value)
