"""Email client factory。"""

from backend.app.infra.email_client import BaseEmailClient, FakeEmailClient, GmailSmtpEmailClient
from backend.app.infra.settings import Settings


def build_email_client(settings: Settings) -> BaseEmailClient:
    """依 settings 建立對應 Email client。"""
    if settings.email_provider == "fake":
        return FakeEmailClient()

    if settings.email_provider == "gmail_smtp":
        username = settings.gmail_smtp_username.strip()
        app_password = settings.gmail_smtp_app_password.strip()
        if not username or not app_password:
            raise ValueError("gmail_smtp 模式需要設定 GMAIL_SMTP_USERNAME 與 GMAIL_SMTP_APP_PASSWORD")

        from_address = settings.email_from_address.strip() or username
        return GmailSmtpEmailClient(
            host=settings.gmail_smtp_host,
            port=settings.gmail_smtp_port,
            username=username,
            app_password=app_password,
            from_name=settings.email_from_name,
            from_address=from_address,
        )

    if settings.email_provider == "production":
        raise NotImplementedError("Production email provider 尚未實作")

    raise ValueError("不支援的 EMAIL_PROVIDER")
