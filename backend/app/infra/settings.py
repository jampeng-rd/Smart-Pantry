"""應用程式設定。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """系統環境設定模型。"""

    app_name: str = "Smart Pantry API"
    database_url: str = (
        "postgresql+psycopg://smartpantry_user:smartpantry_password@localhost:5432/smartpantry_db"
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SMARTPANTRY_")


@lru_cache
def get_settings() -> Settings:
    """取得快取後的系統設定。"""
    return Settings()
