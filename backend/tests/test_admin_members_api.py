"""Admin 會員管理 API 與依賴測試。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from backend.app.admin_api.dependencies import get_current_admin_user_id
from backend.app.admin_api.members import list_members
from backend.app.domain.schemas.admin_member_schema import AdminMemberItem, AdminMemberListResponseData
from backend.app.services.admin_member_service import AdminMemberService


class FakeAdminMemberService(AdminMemberService):
    """測試用 AdminMemberService。"""

    def __init__(self) -> None:
        """建立測試服務實例。"""
        self.last_q: str | None = None

    def ensure_admin_user(self, user_id: int) -> None:
        """模擬 admin 權限檢查。"""
        if user_id != 1:
            raise HTTPException(status_code=403, detail="需要管理員權限")

    def list_members(self, page: int, page_size: int, q: str | None = None) -> AdminMemberListResponseData:
        """回傳固定會員列表。"""
        self.last_q = q
        return AdminMemberListResponseData(
            items=[
                AdminMemberItem(
                    id=1,
                    email="admin@example.com",
                    display_name="管理員",
                    is_admin=True,
                    created_at=datetime.now(timezone.utc),
                )
            ],
            page=page,
            page_size=page_size,
            total=1,
        )


def test_admin_dependency_should_reject_non_admin() -> None:
    """非 admin 應被依賴拒絕。"""
    service = FakeAdminMemberService()
    with pytest.raises(HTTPException) as exc:
        get_current_admin_user_id(user_id=2, service=service)
    assert exc.value.status_code == 403


def test_admin_members_route_should_return_member_list() -> None:
    """admin 可取得會員列表。"""
    service = FakeAdminMemberService()
    response = list_members(page=1, page_size=10, q=None, _=1, service=service)
    payload = response.model_dump()

    assert payload["status"] == "success"
    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["email"] == "admin@example.com"


def test_admin_members_route_should_forward_q_parameter() -> None:
    """會員查詢關鍵字需正確轉交 service。"""
    service = FakeAdminMemberService()
    _ = list_members(page=1, page_size=10, q="Boy", _=1, service=service)
    assert service.last_q == "Boy"
