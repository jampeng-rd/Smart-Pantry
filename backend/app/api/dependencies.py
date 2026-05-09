"""API 依賴注入工具。"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.infra.database import get_db_session
from backend.app.infra.repository.auth_repository import AuthRepository
from backend.app.infra.repository.ai_job_repository import AiJobRepository
from backend.app.infra.repository.pantry_repository import PantryRepository
from backend.app.infra.repository.shopping_repository import ShoppingRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.expiration_service import ExpirationService
from backend.app.services.pantry_service import PantryService
from backend.app.services.recipe_job_service import RecipeJobService
from backend.app.services.shopping_service import ShoppingService


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    """提供 AuthService 依賴。"""
    repository = AuthRepository(db=db)
    return AuthService(auth_repository=repository)


def get_pantry_service(db: Session = Depends(get_db_session)) -> PantryService:
    """提供 PantryService 依賴。"""
    repository = PantryRepository(db=db)
    return PantryService(pantry_repository=repository)


def get_expiration_service(pantry_service: PantryService = Depends(get_pantry_service)) -> ExpirationService:
    """提供 ExpirationService 依賴。"""
    return ExpirationService(pantry_service=pantry_service)


def get_shopping_service(db: Session = Depends(get_db_session)) -> ShoppingService:
    """提供 ShoppingService 依賴。"""
    repository = ShoppingRepository(db=db)
    return ShoppingService(shopping_repository=repository)


def get_recipe_job_service(db: Session = Depends(get_db_session)) -> RecipeJobService:
    """提供 RecipeJobService 依賴。"""
    repository = AiJobRepository(db=db)
    return RecipeJobService(ai_job_repository=repository)


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
