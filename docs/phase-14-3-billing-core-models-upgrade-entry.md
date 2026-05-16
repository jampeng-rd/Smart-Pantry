# Phase 14-3：Billing 核心資料模型與 Upgrade 入口

## 階段目標

本階段建立 Billing 共用基礎，提供 one-time / subscription 後續共用的資料模型與入口，不實作真實扣款。

## 本階段完成項目

1. 建立 Billing 核心資料模型（SQLAlchemy + Alembic）
- `billing_memberships`
- `billing_transactions`
- `billing_webhook_events`

2. 新增 Alembic migration
- revision：`20260516_1900`
- down_revision：`20260515_1401`

3. 後端 Billing 模組骨架
- API：`GET /billing/upgrade`
- Service：`BillingService`
- Repository：`BillingRepository`
- Schema：`BillingUpgradeEntryResponseData`、`BillingMembershipSummary`

4. `BILLING_MODE` 設定與導向規則
- `BILLING_MODE=one_time` → `upgrade_entry_path=/billing/newebpay-one-time`
- `BILLING_MODE=subscription` → `upgrade_entry_path=/billing/newebpay-subscription`

5. 前端 Upgrade 入口
- 新增路由：`/billing/upgrade`
- UserMenu 新增「升級 PRO」入口，位置在 Help 下方、Log out 上方
- 依 backend 回傳 `billing_mode` / `upgrade_entry_path` 顯示導向按鈕

6. 下一階段占位頁（非真實付款）
- `/billing/newebpay-one-time`
- `/billing/newebpay-subscription`

## 資料模型摘要

### billing_memberships
- `user_id`
- `provider`
- `billing_mode`
- `tier`
- `membership_status`
- `started_at` / `ended_at`
- `provider_customer_ref`
- `provider_subscription_ref`
- `created_at` / `updated_at`

### billing_transactions
- `user_id`
- `membership_id`
- `provider`
- `billing_mode`
- `transaction_status`
- `amount` / `currency`
- `external_trade_no`（unique）
- `provider_reference`
- `description`
- `paid_at` / `failed_at`
- `created_at` / `updated_at`

### billing_webhook_events
- `user_id`（nullable）
- `provider`
- `billing_mode`
- `event_type`
- `provider_event_id`
- `event_summary`
- `payload`（保存 provider 原始資料）
- `received_at` / `processed_at`
- `processing_status`
- `error_message`
- `created_at`

## API 回應重點

`GET /billing/upgrade` 回傳：

- `billing_mode`
- `upgrade_entry_path`
- `one_time_entry_path`
- `subscription_entry_path`
- `membership`（`is_pro`、`tier`、`membership_status` 等）
- `message`

## 測試

Backend：
- `backend/tests/test_billing_service.py`
- `backend/tests/test_billing_api.py`
- `backend/tests/test_billing_settings.py`

Frontend：
- `cd frontend && npm run build`

## 階段邊界確認

本階段未實作：
- Phase 14-4 藍新單次付款 runtime
- Phase 14-5 藍新訂閱扣款 runtime
- Phase 14-6 Admin Billing Management runtime
