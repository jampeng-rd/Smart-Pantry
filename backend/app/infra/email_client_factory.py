"""Email client factory。"""

from backend.app.infra.email_client import BaseEmailClient, FakeEmailClient, GmailSmtpEmailClient
from backend.app.infra.resend_email_client import ResendEmailClient
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
        production_provider = settings.production_email_provider.strip().lower()
        if production_provider == "resend":
            api_key = settings.resend_api_key.strip()
            from_address = settings.email_from_address.strip()
            if not api_key:
                raise ValueError("production/resend 模式需要設定 RESEND_API_KEY")
            if not from_address:
                raise ValueError("production/resend 模式需要設定 EMAIL_FROM_ADDRESS")
            return ResendEmailClient(
                api_key=api_key,
                from_name=settings.email_from_name,
                from_address=from_address,
            )
        if production_provider == "sendgrid":
            raise NotImplementedError("SendGrid provider 尚未實作")
        if production_provider == "ses":
            raise NotImplementedError("Amazon SES provider 尚未實作")
        raise ValueError("不支援的 PRODUCTION_EMAIL_PROVIDER，僅允許 resend、sendgrid、ses")

    raise ValueError("不支援的 EMAIL_PROVIDER")
