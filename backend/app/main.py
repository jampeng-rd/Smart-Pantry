"""FastAPI 應用程式進入點。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.auth import router as auth_router
from backend.app.api.error_handlers import register_error_handlers
from backend.app.api.health import router as health_router
from backend.app.api.pantry import router as pantry_router
from backend.app.api.expiration import router as expiration_router
from backend.app.api.shopping import router as shopping_router
from backend.app.api.recipes import router as recipes_router
from backend.app.api.ingredients import router as ingredients_router
from backend.app.infra.database import init_database
from backend.app.infra.settings import get_cors_origin_list, get_settings


def create_app() -> FastAPI:
    """建立並設定 FastAPI 應用程式。"""
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origin_list(settings),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(health_router)
    app.include_router(pantry_router)
    app.include_router(expiration_router)
    app.include_router(shopping_router)
    app.include_router(recipes_router)
    app.include_router(ingredients_router)

    @app.on_event("startup")
    def startup_event() -> None:
        """啟動時建立必要資料表。"""
        init_database()

    return app


app = create_app()
