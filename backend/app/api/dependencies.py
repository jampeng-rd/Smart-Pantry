"""API 依賴注入工具。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.infra.database import get_db_session
from backend.app.infra.storage import LocalStorage

if TYPE_CHECKING:
    from backend.app.services.auth_service import AuthService


_LOCAL_STORAGE = LocalStorage(root_dir="uploads")


def get_auth_service(db: Session = Depends(get_db_session)):
    """提供 AuthService 依賴。"""
    from backend.app.infra.repository.auth_repository import AuthRepository
    from backend.app.services.auth_service import AuthService

    repository = AuthRepository(db=db)
    return AuthService(auth_repository=repository)


def get_pantry_service(db: Session = Depends(get_db_session)):
    """提供 PantryService 依賴。"""
    from backend.app.infra.repository.pantry_repository import PantryRepository
    from backend.app.services.pantry_service import PantryService

    repository = PantryRepository(db=db)
    return PantryService(pantry_repository=repository)


def get_expiration_service(pantry_service=Depends(get_pantry_service)):
    """提供 ExpirationService 依賴。"""
    from backend.app.services.expiration_service import ExpirationService

    return ExpirationService(pantry_service=pantry_service)


def get_shopping_service(db: Session = Depends(get_db_session)):
    """提供 ShoppingService 依賴。"""
    from backend.app.infra.repository.shopping_repository import ShoppingRepository
    from backend.app.services.shopping_service import ShoppingService

    repository = ShoppingRepository(db=db)
    return ShoppingService(shopping_repository=repository)


def get_recipe_job_service(db: Session = Depends(get_db_session)):
    """提供 RecipeJobService 依賴。"""
    from backend.app.infra.repository.ai_job_repository import AiJobRepository
    from backend.app.services.recipe_job_service import RecipeJobService

    repository = AiJobRepository(db=db)
    return RecipeJobService(ai_job_repository=repository)


def get_ingredient_photo_job_service(db: Session = Depends(get_db_session)):
    """提供 IngredientPhotoJobService 依賴。"""
    from backend.app.infra.repository.ai_job_repository import AiJobRepository
    from backend.app.services.ingredient_photo_job_service import IngredientPhotoJobService

    repository = AiJobRepository(db=db)
    return IngredientPhotoJobService(ai_job_repository=repository, storage=_LOCAL_STORAGE)


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    """從 Authorization Header 擷取 Bearer token。"""
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少授權資訊")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="授權格式錯誤")
    return authorization[len(prefix) :]


def get_current_user_id(
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> int:
    """取得目前登入使用者 ID。"""
    return auth_service.get_current_user_id(access_token=access_token)
