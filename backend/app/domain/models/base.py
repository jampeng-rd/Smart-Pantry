"""SQLAlchemy Base 定義。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 SQLAlchemy Model 的共用基底類別。"""
