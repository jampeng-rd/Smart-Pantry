"""Pantry 授權依賴測試。"""

import pytest
from fastapi import HTTPException

from backend.app.api.dependencies import get_bearer_token


def test_unauthorized_should_fail_when_missing_header() -> None:
    """未登入時應回傳 401。"""
    with pytest.raises(HTTPException) as exc:
        get_bearer_token(authorization=None)
    assert exc.value.status_code == 401
