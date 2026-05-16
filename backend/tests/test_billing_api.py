"""Billing API 路由測試。"""

from __future__ import annotations

from backend.app.api.billing import get_billing_upgrade_entry
from backend.app.domain.schemas.billing_schema import BillingMembershipSummary, BillingUpgradeEntryResponseData
from backend.app.services.billing_service import BillingService


class FakeBillingService(BillingService):
    """測試用 BillingService。"""

    def __init__(self) -> None:
        self.last_user_id: int | None = None

    def get_upgrade_entry(self, user_id: int) -> BillingUpgradeEntryResponseData:
        """回傳固定升級入口資料。"""
        self.last_user_id = user_id
        return BillingUpgradeEntryResponseData(
            billing_mode="one_time",
            upgrade_entry_path="/billing/newebpay-one-time",
            one_time_entry_path="/billing/newebpay-one-time",
            subscription_entry_path="/billing/newebpay-subscription",
            membership=BillingMembershipSummary(
                is_pro=False,
                tier="FREE",
                membership_status="inactive",
                provider=None,
                billing_mode=None,
                started_at=None,
                ended_at=None,
            ),
            message="目前為單次付款模式，將導向藍新單次付款入口。",
        )


def test_billing_upgrade_route_should_return_success_payload() -> None:
    """升級入口 API 應回傳統一格式。"""
    service = FakeBillingService()

    response = get_billing_upgrade_entry(user_id=1, service=service)
    payload = response.model_dump()

    assert payload["status"] == "success"
    assert payload["data"]["billing_mode"] == "one_time"
    assert payload["data"]["upgrade_entry_path"] == "/billing/newebpay-one-time"
    assert service.last_user_id == 1
