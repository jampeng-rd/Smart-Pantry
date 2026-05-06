"""資料庫連線與 Session Factory 集中管理。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infra.settings import get_settings

settings = get_settings()

# 集中建立單一 Engine，避免每次請求重建連線池。
engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    """提供資料庫 Session 依賴。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
