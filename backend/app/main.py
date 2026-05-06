"""FastAPI 應用程式進入點。"""

from fastapi import FastAPI

from backend.app.api.health import router as health_router
from backend.app.infra.settings import get_settings


def create_app() -> FastAPI:
    """建立並設定 FastAPI 應用程式。"""
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    return app


app = create_app()
