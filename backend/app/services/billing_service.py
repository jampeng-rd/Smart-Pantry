"""Billing 商業邏輯服務。"""

from fastapi import HTTPException, status

from backend.app.domain.schemas.billing_schema import BillingMembershipSummary, BillingUpgradeEntryResponseData
from backend.app.infra.repository.billing_repository import BillingRepository
from backend.app.infra.settings import Settings


class BillingService:
    """處理升級入口與會員狀態查詢。"""

    def __init__(self, repository: BillingRepository, settings: Settings):
        """建立服務實例。"""
        self.repository = repository
        self.settings = settings

    def get_upgrade_entry(self, user_id: int) -> BillingUpgradeEntryResponseData:
        """取得升級入口設定與目前會員狀態。"""
        user = self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        membership = self.repository.get_latest_membership(user_id=user_id)
        summary = BillingMembershipSummary(
            is_pro=bool(membership and membership.tier.upper() == "PRO" and membership.membership_status in {"active", "trialing"}),
            tier=membership.tier if membership else "FREE",
            membership_status=membership.membership_status if membership else "inactive",
            provider=membership.provider if membership else None,
            billing_mode=membership.billing_mode if membership else None,
            started_at=membership.started_at if membership else None,
            ended_at=membership.ended_at if membership else None,
        )

        if self.settings.billing_mode == "one_time":
            entry_path = "/billing/newebpay-one-time"
            message = "目前為單次付款模式，將導向藍新單次付款入口。"
        else:
            entry_path = "/billing/newebpay-subscription"
            message = "目前為訂閱制模式，將導向藍新訂閱付款入口。"

        return BillingUpgradeEntryResponseData(
            billing_mode=self.settings.billing_mode,
            upgrade_entry_path=entry_path,
            one_time_entry_path="/billing/newebpay-one-time",
            subscription_entry_path="/billing/newebpay-subscription",
            membership=summary,
            message=message,
        )
