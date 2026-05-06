"""API 依賴注入工具。"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.infra.database import get_db_session
from backend.app.infra.repository.auth_repository import AuthRepository
from backend.app.services.auth_service import AuthService


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    """提供 AuthService 依賴。"""
    repository = AuthRepository(db=db)
    return AuthService(auth_repository=repository)


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    """從 Authorization Header 擷取 Bearer token。"""
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少授權資訊")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="授權格式錯誤")
    return authorization[len(prefix) :]
