"""Billing API 路由測試。"""

from __future__ import annotations

from backend.app.api.billing import (
    create_newebpay_one_time_checkout,
    get_billing_upgrade_entry,
    get_newebpay_one_time_transaction_status,
    handle_newebpay_return,
)
from backend.app.domain.schemas.billing_schema import (
    BillingMembershipSummary,
    BillingOneTimeCheckoutResponseData,
    BillingTransactionStatusResponseData,
    BillingUpgradeEntryResponseData,
)
from backend.app.services.billing_service import BillingService


class FakeBillingService(BillingService):
    """測試用 BillingService。"""

    def __init__(self) -> None:
        self.last_user_id: int | None = None

    def get_upgrade_entry(self, user_id: int) -> BillingUpgradeEntryResponseData:
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

    def create_newebpay_one_time_checkout(self, user_id: int) -> BillingOneTimeCheckoutResponseData:
        self.last_user_id = user_id
        return BillingOneTimeCheckoutResponseData(
            transaction_id=1,
            external_trade_no="SP120260516000001",
            gateway_url="https://ccore.newebpay.com/MPG/mpg_gateway",
            merchant_id="MS123456789",
            trade_info="abc",
            trade_sha="def",
            version="2.2",
        )

    def get_transaction_status(self, user_id: int, external_trade_no: str) -> BillingTransactionStatusResponseData:
        self.last_user_id = user_id
        return BillingTransactionStatusResponseData(
            external_trade_no=external_trade_no,
            transaction_status="success",
            membership_status="active",
            is_pro=True,
            amount=99.0,
            paid_at=None,
            failed_at=None,
        )

    def build_newebpay_return_redirect_url(self, payload: dict) -> str:
        return f"https://example.com/result?external_trade_no={payload.get('MerchantOrderNo', '')}"


def test_billing_upgrade_route_should_return_success_payload() -> None:
    service = FakeBillingService()
    response = get_billing_upgrade_entry(user_id=1, service=service)
    payload = response.model_dump()
    assert payload["status"] == "success"
    assert payload["data"]["billing_mode"] == "one_time"


def test_billing_checkout_route_should_return_gateway_payload() -> None:
    service = FakeBillingService()
    response = create_newebpay_one_time_checkout(user_id=1, service=service)
    payload = response.model_dump()
    assert payload["status"] == "success"
    assert payload["data"]["gateway_url"] == "https://ccore.newebpay.com/MPG/mpg_gateway"


def test_billing_transaction_status_route_should_return_data() -> None:
    service = FakeBillingService()
    response = get_newebpay_one_time_transaction_status(external_trade_no="SP123", user_id=1, service=service)
    payload = response.model_dump()
    assert payload["status"] == "success"
    assert payload["data"]["external_trade_no"] == "SP123"
    assert payload["data"]["is_pro"] is True


class FakeRequest:
    """測試用 request form stub。"""

    async def form(self) -> dict[str, str]:
        return {"MerchantOrderNo": "SP123"}


def test_billing_return_route_should_redirect_to_frontend_result_page() -> None:
    import asyncio

    service = FakeBillingService()
    response = asyncio.run(handle_newebpay_return(request=FakeRequest(), service=service))
    assert response.status_code == 303
    assert response.headers["location"] == "https://example.com/result?external_trade_no=SP123"
