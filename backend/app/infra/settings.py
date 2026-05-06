"""應用程式設定。"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """系統環境設定模型。"""

    app_name: str = "Smart Pantry API"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://smartpantry_user:smartpantry_password@localhost:5432/smartpantry_db"

    jwt_secret_key: str = "change-me-in-local-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"
    vite_api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        """驗證 CORS 字串不可為空。"""
        if not value.strip():
            raise ValueError("CORS_ORIGINS 不可為空")
        return value


def get_cors_origin_list(settings: Settings) -> list[str]:
    """將逗號分隔的 CORS 設定轉為陣列。"""
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """取得快取後的系統設定。"""
    return Settings()
