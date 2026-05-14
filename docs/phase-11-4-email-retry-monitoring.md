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
