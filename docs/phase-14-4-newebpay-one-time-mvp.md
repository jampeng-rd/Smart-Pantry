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
- `NEWEBPAY_RETURN_URL`
- `NEWEBPAY_CUSTOMER_BACK_URL`

部署 URL：

- `NEWEBPAY_NOTIFY_URL=https://smart-pantry-backend-41lm.onrender.com/billing/newebpay/notify`
- `NEWEBPAY_RETURN_URL=https://smart-pantry-henna.vercel.app/billing/newebpay-one-time/result`
- `NEWEBPAY_CUSTOMER_BACK_URL=https://smart-pantry-henna.vercel.app/billing/upgrade`
