"""資料庫連線與 Session Factory 集中管理。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.domain.models import Base
from backend.app.infra.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    """提供資料庫 Session 依賴。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """初始化資料庫連線（Phase 12-1 起由 Alembic 管理 schema）。"""
    # Phase 12-1 起不再於啟動時自動 create_all，避免繞過 migration 流程。
    return None
