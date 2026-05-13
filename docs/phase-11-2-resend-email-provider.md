# Phase 11-2：Production Email Provider - Resend

## 概要

本階段在既有 `BaseEmailClient` 抽象下，新增正式環境可用的 Resend provider，並保持 provider 分層，避免 service 層直接綁定特定廠商。

## 本階段範圍

- 實作：Resend
- 不實作：SendGrid、Amazon SES
- 不做：正式 scheduler/cron（Phase 11-3）
- 不做：retry/monitoring（Phase 11-4）

## 設定規則

- `EMAIL_PROVIDER`：`fake` / `gmail_smtp` / `production`
- `PRODUCTION_EMAIL_PROVIDER`：`resend` / `sendgrid` / `ses`
- production provider 三選一，不需要同時申請三組 provider。
- Phase 11-2 目前只支援 `resend`。

必要欄位：

- `EMAIL_PROVIDER=production` 時，`EMAIL_FROM_ADDRESS` 不可為空。
- `EMAIL_PROVIDER=production` 且 `PRODUCTION_EMAIL_PROVIDER=resend` 時，`RESEND_API_KEY` 不可為空。

## 架構與實作

- 新增：`backend/app/infra/resend_email_client.py`
  - `ResendEmailClient` 使用 HTTP API 呼叫 `POST /emails`
  - 輸入：`to/subject/text`，寄件者由 `EMAIL_FROM_NAME + EMAIL_FROM_ADDRESS` 組合
  - 成功：`EmailSendResult(success=True)`
  - 失敗：`EmailSendResult(success=False, error_message=中文友善訊息)`
  - 錯誤訊息不含 `RESEND_API_KEY`
- 保留：`GmailSmtpEmailClient` 於 `backend/app/infra/email_client.py`
- 更新：`backend/app/infra/email_client_factory.py`
  - `fake` -> `FakeEmailClient`
  - `gmail_smtp` -> `GmailSmtpEmailClient`
  - `production + resend` -> `ResendEmailClient`
  - `production + sendgrid/ses` -> 明確「尚未實作」
- 更新：`backend/app/services/expiration_email_reminder_service.py`
  - subject：`【智慧食材保存系統】食材即將到期提醒`
  - body：純文字表格（目前不引入 HTML email）
  - 欄位包含：`食材名稱 / 數量 / 單位 / 保存位置`
  - 前文已顯示「以下是 <target_expiration_date> 即將到期的食材」，表格不重複放到期日欄位
  - quantity 顯示規則：整數顯示 `1`、`2`；有小數才顯示如 `1.5`
  - `storage_location` 空值時顯示 `未設定`
  - 結尾固定：`此提醒來自【智慧食材保存與膳食管理系統】自動發送，無需回信。`
  - 後續可新增 HTML email template，讓表格視覺更完整

## 安全注意事項

- `RESEND_API_KEY` 僅能放 `.env` 或部署平台 secret manager。
- 不可把 API key 提交到 git。
- log、exception、delivery log error_message 不可包含 API key。
- Resend 需要 verified domain 或 Resend 允許的 sender。

## 測試策略

- 單元測試不可真的呼叫 Resend API。
- Resend client 以 mock/stub HTTP 驗證：
  - payload 是否包含 `from/to/subject/text`
  - 失敗時 error_message 不含 API key
- factory/settings 測試覆蓋：
  - production + resend 成功建立 client
  - 缺少 `RESEND_API_KEY` 錯誤
  - 缺少 `EMAIL_FROM_ADDRESS` 錯誤
  - `sendgrid/ses` 尚未實作錯誤
  - 不支援 `PRODUCTION_EMAIL_PROVIDER` 錯誤

## 手動測試步驟（Resend）

1. `.env` 設定：
   - `EMAIL_PROVIDER=production`
   - `PRODUCTION_EMAIL_PROVIDER=resend`
   - `RESEND_API_KEY=<your_key>`
   - `EMAIL_FROM_NAME=Smart Pantry`
   - `EMAIL_FROM_ADDRESS=<verified_sender@example.com>`
2. 準備提醒資料：
   - 使用者 reminder 設為 `1` 或 `3`
   - 建立對應到期日的 pantry item
3. 執行：
   - `python -m backend.app.jobs.expiration_email_runner --send-window morning_08 --scheduled-date 2026-05-13`
4. 驗證：
   - runner summary `success_count` > 0
   - delivery log 出現 `success`
   - 收件匣收到提醒信

## 本地 Debug 指令（provider/factory/resend）

可直接使用目前 `.env` 設定透過 factory 建立實際 client，送一封最小測試信：

```bash
python -m backend.app.jobs.email_provider_debug --to your_email@example.com
```

觀察 log 重點：

- factory 會印出 `provider / production_provider / from_address / client_class`
- resend client 會印出呼叫前後與失敗摘要（不含 API key）
- 若是 Resend HTTPError，`error_message` 會包含 `HTTP status + Resend 原始 message/error/name 摘要`
