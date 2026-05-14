# Phase 11-4：Email Retry / Failure Handling / Monitoring

## 目標

提升到期提醒 Email delivery reliability，在不改動 reminder 商業規則（`reminder_days`、`duplicate protection`、`send_window`、`scheduled_date`）前提下補齊 retry、錯誤分類與監控 log。

## 本階段內容

- 新增 `EMAIL_RETRY_MAX_ATTEMPTS`（預設 `1`，允許 `0~3`）
- timeout / network / provider 5xx 才可 retry
- provider 4xx、收件者/寄件者/domain 驗證/設定錯誤不可 retry
- delivery log 擴充：`attempt_count`、`last_error_message`、`last_attempt_at`、`final_status`
- runner summary 新增：`retry_count`、`permanent_failed_count`
- 新增 structured monitoring logs：
  - `email send retry`
  - `email temporary failure`
  - `email permanent failure`

## Retry 策略

- `EMAIL_RETRY_MAX_ATTEMPTS=0`：不重試
- `EMAIL_RETRY_MAX_ATTEMPTS=1`：失敗後最多補發 1 次（預設）
- `EMAIL_RETRY_MAX_ATTEMPTS=2`：最多補發 2 次
- `EMAIL_RETRY_MAX_ATTEMPTS=3`：最多補發 3 次
- 超過 3：Settings 驗證失敗

固定 backoff：

- 第 1 次 retry：5 秒
- 第 2 次 retry：15 秒
- 第 3 次 retry：30 秒

## 錯誤分類

`EmailSendResult` 新增欄位：

- `success`
- `should_retry`
- `error_category`：`timeout` / `network_error` / `provider_4xx` / `provider_5xx` / `invalid_configuration` / `unknown_error`
- `error_message`

重試條件：

- `timeout`
- `network_error`
- `provider_5xx`

不重試條件：

- `provider_4xx`
- `invalid_configuration`（例如 invalid recipient / invalid sender / verified domain 不符）
- 其他明確不可重試錯誤

此策略可避免使用者 email 設定錯誤時反覆寄送，降低 provider 成本與封鎖風險。

## Timeout

- Resend `urlopen(timeout=30)`
- Gmail SMTP `smtplib.SMTP(..., timeout=30)`

## Delivery log 擴充

`expiration_reminder_deliveries` 新增：

- `attempt_count`
- `last_error_message`
- `last_attempt_at`
- `final_status`：`success` / `failed` / `permanent_failed`

語意：

- `failed`：暫時失敗，仍可能重試
- `permanent_failed`：不可重試或已達最大重試次數
- `success`：寄送成功

## 監控 log（structured）

本階段只做應用層 structured log，不新增 metrics server / alert service。

安全要求：

- log 不可包含 API key、Authorization header、SMTP password 或其他 secret

## 本階段不做

- queue/broker（Celery/Redis/RabbitMQ）
- admin dashboard
- metrics server / websocket / dead letter queue
- 前端 retry UI

## 驗證

- `python -m compileall -q backend/app`
- `.venv/bin/python -m pytest backend/tests -q`
- `cd frontend && npm run build`

## Email Delivery UX 修正（同 Phase 11-4）

為避免暴露 provider 維運資訊，`Settings > 最近寄送紀錄` 改為只顯示使用者友善訊息：

- permanent failure：`此 Email 無法正確寄送通知，若有問題請來信諮詢。`
- temporary failure：`信件通知服務暫時無法使用，系統維護中...`
- client network failure（前端網路異常）：`網路異常，請稍後再試。`

後端保留完整錯誤（`last_error_message`、`error_category`、provider response、structured logs）供未來 admin/monitoring 使用；但 user API 僅回傳 `user_friendly_error_message`，不回傳 provider 原始錯誤內容。

前端規範：

- table / mobile accordion / 狀態顯示 / API 錯誤提示均使用 `user_friendly_error_message` 或網路統一文案
- 不顯示 HTTP status、provider 名稱、SMTP exception、traceback、provider 英文訊息

## Email Delivery UX 錯誤分類修正（Phase 11-4 同階段）

使用者可見訊息調整為四類：

1. 使用者 Email 無法寄送
- 訊息：`此 Email 無法正確寄送通知，若有問題請來信諮詢。`
- 例：invalid recipient、收件者信箱不可用

2. 信件服務暫時不可用
- 訊息：`信件通知服務暫時無法使用，系統維護中...`
- 例：timeout、network_error、provider_5xx、retry 中

3. 使用者前端網路異常
- 訊息：`網路異常，請稍後再試。`
- 例：Failed to fetch、NetworkError、瀏覽器無法連 backend

4. 系統設定或伺服器異常
- 訊息：`目前系統偵測異常，系統維修中。`
- 例：API key invalid、domain not verified、invalid from/sender、provider 設定錯誤、backend 500

後端仍保留完整錯誤細節於 delivery log / structured logs；使用者 API 僅回傳 `user_friendly_error_message`。
