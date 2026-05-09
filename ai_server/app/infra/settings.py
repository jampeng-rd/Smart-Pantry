"""AI Server 設定。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AiServerSettings(BaseSettings):
    """AI server / worker 環境設定。"""

    app_name: str = "Smart Pantry AI Server"
    ai_server_host: str = "0.0.0.0"
    ai_server_port: int = 8100

    database_url: str = "postgresql+psycopg://smartpantry_user:smartpantry_password@localhost:5432/smartpantry_db"

    ai_worker_poll_interval_seconds: int = 5
    ai_worker_batch_size: int = 1
    ai_job_timeout_seconds: int = 300

    ollama_base_url: str = "http://localhost:11434"
    llm_text_model: str = "qwen2.5:7b"
    llm_vision_model: str = "qwen3-vl:8b"

    # ai_server 與 backend 目前共用同一份 .env。
    # 為避免 backend/frontend 專用變數（例如 JWT、CORS）造成啟動失敗，
    # ai_server settings 僅定義自身需要欄位，並忽略其餘 env。
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> AiServerSettings:
    """取得快取後的 AI server 設定。"""
    return AiServerSettings()
