"""應用程式設定。"""

from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EmailProvider = str


class Settings(BaseSettings):
    """系統環境設定模型。"""

    app_name: str = "Smart Pantry API"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    scheduler_timezone: str = "Asia/Taipei"

    database_url: str = "postgresql+psycopg://smartpantry_user:smartpantry_password@localhost:5432/smartpantry_db"

    jwt_secret_key: str = "change-me-in-local-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"
    vite_api_base_url: str = "http://localhost:8000"

    # Phase 08 AI job/worker 共用設定（backend 需能讀取，避免 .env 驗證失敗）
    ai_server_host: str = "0.0.0.0"
    ai_server_port: int = 8100
    ai_worker_poll_interval_seconds: int = 5
    ai_worker_batch_size: int = 1
    ai_worker_job_types: str = "recipe_recommendation"
    ai_job_timeout_seconds: int = 300
    ai_vision_timeout_seconds: int = 60
    ollama_base_url: str = "http://localhost:11434"
    ollama_text_base_url: str = ""
    ollama_vision_base_url: str = ""
    llm_text_model: str = "qwen2.5:7b"
    llm_vision_model: str = "qwen3-vl:8b"

    # Phase 11 Email provider 設定
    email_provider: EmailProvider = "fake"
    email_from_name: str = "Smart Pantry"
    email_from_address: str = "no-reply@example.com"
    gmail_smtp_host: str = "smtp.gmail.com"
    gmail_smtp_port: int = 587
    gmail_smtp_username: str = ""
    gmail_smtp_app_password: str = ""
    production_email_provider: str = "resend"
    resend_api_key: str = ""
    sendgrid_api_key: str = ""
    aws_ses_region: str = ""
    aws_ses_access_key_id: str = ""
    aws_ses_secret_access_key: str = ""
    email_retry_max_attempts: int = 1

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        """驗證 CORS 字串不可為空。"""
        if not value.strip():
            raise ValueError("CORS_ORIGINS 不可為空")
        return value

    @field_validator("email_provider")
    @classmethod
    def validate_email_provider(cls, value: str) -> str:
        """驗證 EMAIL_PROVIDER 僅允許 fake/gmail_smtp/production。"""
        allowed = {"fake", "gmail_smtp", "production"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("EMAIL_PROVIDER 僅允許 fake、gmail_smtp、production")
        return normalized

    @field_validator("production_email_provider")
    @classmethod
    def validate_production_email_provider(cls, value: str) -> str:
        """驗證 PRODUCTION_EMAIL_PROVIDER 值。"""
        normalized = value.strip().lower()
        allowed = {"resend", "sendgrid", "ses"}
        if normalized not in allowed:
            raise ValueError("PRODUCTION_EMAIL_PROVIDER 僅允許 resend、sendgrid、ses")
        return normalized

    @model_validator(mode="after")
    def validate_email_provider_requirements(self):
        """驗證不同 Email provider 模式的必要欄位。"""
        if self.email_retry_max_attempts < 0 or self.email_retry_max_attempts > 3:
            raise ValueError("EMAIL_RETRY_MAX_ATTEMPTS 僅允許 0 到 3")
        if self.email_provider == "production":
            if not self.email_from_address.strip():
                raise ValueError("EMAIL_PROVIDER=production 時，EMAIL_FROM_ADDRESS 不可為空")
            if self.production_email_provider == "resend" and not self.resend_api_key.strip():
                raise ValueError("EMAIL_PROVIDER=production 且 PRODUCTION_EMAIL_PROVIDER=resend 時，RESEND_API_KEY 不可為空")
        return self


def get_cors_origin_list(settings: Settings) -> list[str]:
    """將逗號分隔的 CORS 設定轉為陣列。"""
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """取得快取後的系統設定。"""
    return Settings()
