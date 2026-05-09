"""AI Server 入口。"""

from fastapi import FastAPI

from ai_server.app.infra.settings import get_settings


def create_app() -> FastAPI:
    """建立 AI server 應用程式。"""
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    def health() -> dict:
        """提供 AI server 健康檢查。"""
        return {"status": "ok", "service": "smartpantry-ai-server"}

    return app


app = create_app()
