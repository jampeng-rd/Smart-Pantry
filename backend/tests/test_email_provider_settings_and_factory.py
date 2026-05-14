"""Email provider settings 與 factory 測試。"""

from __future__ import annotations

from typing import get_type_hints

import pytest

from backend.app.infra.email_client import FakeEmailClient, GmailSmtpEmailClient
from backend.app.infra.email_client_factory import build_email_client
from backend.app.infra.resend_email_client import ResendEmailClient
from backend.app.infra.settings import Settings
from backend.app.services.expiration_email_reminder_service import ExpirationEmailReminderService


def test_settings_should_read_email_provider_fake() -> None:
    """Settings 應可讀取 EMAIL_PROVIDER=fake。"""
    settings = Settings(email_provider="fake")
    assert settings.email_provider == "fake"
    assert settings.email_retry_max_attempts == 1


def test_settings_should_accept_retry_max_attempts_from_env(monkeypatch) -> None:
    """EMAIL_RETRY_MAX_ATTEMPTS 應可由 env 覆寫。"""
    monkeypatch.setenv("EMAIL_RETRY_MAX_ATTEMPTS", "3")
    settings = Settings()
    assert settings.email_retry_max_attempts == 3


def test_settings_should_reject_retry_max_attempts_greater_than_3() -> None:
    """EMAIL_RETRY_MAX_ATTEMPTS 不可超過 3。"""
    with pytest.raises(ValueError) as exc:
        Settings(email_retry_max_attempts=4)
    assert "EMAIL_RETRY_MAX_ATTEMPTS" in str(exc.value)


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


def test_factory_log_should_not_include_secret_for_production_resend(caplog) -> None:
    """factory 安全 log 應包含 provider 與 client class，且不可含 API key。"""
    settings = Settings(
        email_provider="production",
        production_email_provider="resend",
        email_from_name="Smart Pantry",
        email_from_address="no-reply@example.com",
        resend_api_key="re_test_secret_key",
    )
    with caplog.at_level("INFO"):
        client = build_email_client(settings)

    assert isinstance(client, ResendEmailClient)
    assert "provider=production" in caplog.text
    assert "production_provider=resend" in caplog.text
    assert "client_class=ResendEmailClient" in caplog.text
    assert "re_test_secret_key" not in caplog.text


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


def test_factory_should_return_resend_client_when_production_resend() -> None:
    """production + resend 時，factory 應回 ResendEmailClient。"""
    settings = Settings(
        email_provider="production",
        production_email_provider="resend",
        email_from_name="Smart Pantry",
        email_from_address="no-reply@example.com",
        resend_api_key="re_test_123",
    )
    client = build_email_client(settings)
    assert isinstance(client, ResendEmailClient)
    assert client.from_address == "no-reply@example.com"


def test_settings_should_fail_when_production_resend_missing_api_key() -> None:
    """production + resend 缺少 API key 應回中文友善錯誤。"""
    with pytest.raises(ValueError) as exc:
        Settings(
            email_provider="production",
            production_email_provider="resend",
            email_from_address="no-reply@example.com",
            resend_api_key="",
        )
    assert "RESEND_API_KEY" in str(exc.value)


def test_settings_should_fail_when_production_missing_from_address() -> None:
    """production 模式缺少寄件地址應回中文友善錯誤。"""
    with pytest.raises(ValueError) as exc:
        Settings(
            email_provider="production",
            production_email_provider="resend",
            email_from_address="",
            resend_api_key="re_test_123",
        )
    assert "EMAIL_FROM_ADDRESS" in str(exc.value)


def test_factory_should_raise_not_implemented_for_sendgrid() -> None:
    """production + sendgrid 應回尚未實作。"""
    settings = Settings(
        email_provider="production",
        production_email_provider="sendgrid",
        email_from_address="no-reply@example.com",
    )
    with pytest.raises(NotImplementedError) as exc:
        build_email_client(settings)
    assert "SendGrid provider 尚未實作" in str(exc.value)


def test_factory_should_raise_not_implemented_for_ses() -> None:
    """production + ses 應回尚未實作。"""
    settings = Settings(
        email_provider="production",
        production_email_provider="ses",
        email_from_address="no-reply@example.com",
    )
    with pytest.raises(NotImplementedError) as exc:
        build_email_client(settings)
    assert "Amazon SES provider 尚未實作" in str(exc.value)


def test_factory_should_raise_friendly_error_for_unsupported_production_provider() -> None:
    """不支援的 production provider 應回中文友善錯誤。"""
    with pytest.raises(ValueError) as exc:
        Settings(
            email_provider="production",
            production_email_provider="mailgun",
            email_from_address="no-reply@example.com",
        )
    assert "PRODUCTION_EMAIL_PROVIDER" in str(exc.value)


def test_expiration_reminder_service_should_only_depend_on_base_email_client() -> None:
    """提醒服務建構子應只依賴 BaseEmailClient 抽象，不綁定 Resend。"""
    annotation_name = get_type_hints(ExpirationEmailReminderService.__init__)["email_client"].__name__
    assert annotation_name == "BaseEmailClient"
