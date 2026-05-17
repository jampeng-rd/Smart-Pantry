# Phase 14-4：藍新單次付款（one-time）MVP

## 目標

完成藍新測試環境單次付款流程（信用卡一次付清）：

1. `/billing/upgrade` 導向 `/billing/newebpay-one-time`
2. 建立交易並跳轉藍新付款頁
3. 付款後接收 notify/callback
4. 更新 transaction/membership 並在前端結果頁顯示狀態

## 後端實作

- `POST /billing/newebpay/one-time/checkout`
  - 建立 `billing_transactions`（`pending`）
  - 產生 `TradeInfo`、`TradeSha`
  - 回傳 `gateway_url` 與送單欄位
- `POST /billing/newebpay/notify`
  - 驗證 `TradeSha`
  - 解密 `TradeInfo`
  - 寫入 `billing_webhook_events`
  - 依通知結果更新 `billing_transactions`
  - 成功時啟用 PRO 會員
- `POST /billing/newebpay/return`
  - 接收藍新前台返回（form POST）
  - 解析 `MerchantOrderNo` / `TradeInfo`
  - 303 redirect 到前端結果頁並帶 `external_trade_no`
- `GET /billing/newebpay/one-time/transactions/{external_trade_no}`
  - 供結果頁查詢交易狀態
  - 強制 `user_id` 隔離

## 前端實作

- `/billing/newebpay-one-time`
  - 顯示方案資訊
  - 呼叫 checkout API
  - 以前端動態 form `POST` 到藍新 gateway
- `/billing/newebpay-one-time/result`
  - 讀取 `external_trade_no`
  - 查詢 backend 交易狀態
  - 顯示 `success / failed / pending`
- `/billing/upgrade`
  - 顯示目前會員狀態（`is_pro`、`tier`、`membership_status`）
  - PRO active 顯示已升級文案

## Phase 14-4 收尾（UI / 顯示規則）

- `/billing/newebpay-one-time/result`
  - TopToolbar 標題為 `單次付款結果`
  - 內容區不重複顯示同名 `workspace-title`
- billing 會員狀態前端顯示改為繁中：
  - `active` → `啟用`
  - 其他狀態 → `未啟用`
- `/admin/members` API 補最小必要欄位：
  - `is_pro`
  - `membership_status`
- `/admin/members` 角色顯示規則：
  - `is_admin=true` → `管理員`
  - `is_admin=false` 且 `is_pro=true` → `PRO`
  - 其他 → `一般會員`
- `PRO` badge 使用黃色系小圓角樣式，且管理員/一般會員 badge 樣式維持不變。

## one-time PRO 規則（本階段）

- 採 **永久 PRO（ended_at=null）**。
- 理由：Phase 14-4 僅實作單次付款 MVP，尚未進入訂閱續扣與到期管理（Phase 14-5）。

## Idempotency

- 以 `external_trade_no`（MerchantOrderNo）對應交易。
- 若交易已為 `success`，同筆 notify 重送時只記錄 webhook event，不重複升級 membership。

## 環境變數

- `NEWEBPAY_ENV=test|production`
- `NEWEBPAY_MERCHANT_ID`
- `NEWEBPAY_HASH_KEY`
- `NEWEBPAY_HASH_IV`
- `NEWEBPAY_MPG_VERSION`
- `NEWEBPAY_NOTIFY_URL`
- `NEWEBPAY_RETURN_URL`（backend return endpoint）
- `NEWEBPAY_FRONTEND_RESULT_URL`（frontend result page）
- `NEWEBPAY_CUSTOMER_BACK_URL`

部署 URL：

- `NEWEBPAY_NOTIFY_URL=https://smart-pantry-backend-41lm.onrender.com/billing/newebpay/notify`
- `NEWEBPAY_RETURN_URL=https://smart-pantry-backend-41lm.onrender.com/billing/newebpay/return`
- `NEWEBPAY_FRONTEND_RESULT_URL=https://smart-pantry-henna.vercel.app/billing/newebpay-one-time/result`
- `NEWEBPAY_CUSTOMER_BACK_URL=https://smart-pantry-henna.vercel.app/billing/upgrade`
