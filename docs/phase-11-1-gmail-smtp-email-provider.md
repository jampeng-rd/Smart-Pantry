# Phase 11-1：Gmail SMTP 真實寄信

## 概要

本階段在既有 `BaseEmailClient / FakeEmailClient` 架構上，新增 Gmail SMTP 實作與 provider factory，讓 `EMAIL_PROVIDER` 可切換 `fake` 與 `gmail_smtp`。

## Provider 模式

- `fake`：預設，不寄真信。
- `gmail_smtp`：透過 Gmail SMTP 真實寄信（開發/測試/少量寄送）。
- `production`：本階段回明確「尚未實作」，留待 Phase 11-2。

## 設定調整

新增並支援以下 env：

- `EMAIL_PROVIDER`
- `EMAIL_FROM_NAME`
- `EMAIL_FROM_ADDRESS`
- `GMAIL_SMTP_HOST`
- `GMAIL_SMTP_PORT`
- `GMAIL_SMTP_USERNAME`
- `GMAIL_SMTP_APP_PASSWORD`
- `PRODUCTION_EMAIL_PROVIDER`
- `RESEND_API_KEY`
- `SENDGRID_API_KEY`
- `AWS_SES_REGION`
- `AWS_SES_ACCESS_KEY_ID`
- `AWS_SES_SECRET_ACCESS_KEY`

規則：

- `EMAIL_PROVIDER` 僅允許 `fake/gmail_smtp/production`。
- `gmail_smtp` 需 `GMAIL_SMTP_USERNAME` 與 `GMAIL_SMTP_APP_PASSWORD`。
- `EMAIL_FROM_ADDRESS` 可為空，空值時 fallback 為 `GMAIL_SMTP_USERNAME`。

## Gmail SMTP 實作

- 使用 Python 標準庫 `smtplib` 與 `email.message.EmailMessage`。
- 連線流程：`SMTP(host, port)` -> `STARTTLS` -> `login` -> `send_message`。
- 寄件人格式：`EMAIL_FROM_NAME <EMAIL_FROM_ADDRESS>`。
- 失敗回傳友善錯誤訊息，不包含密碼或 secret。

## Runner 串接

`expiration_email_runner` 改為透過 email client factory 建立 provider。

- `fake`：維持不寄真信。
- `gmail_smtp`：實際透過 SMTP 寄信。
- `production`：立即回尚未實作錯誤。

## 測試策略

- 單元測試不可寄真信。
- Gmail SMTP 測試以 stub SMTP server 驗證 subject/to/from/body 與失敗路徑。
- 既有 Phase 10-2/10-3 reminder 測試需持續通過。

## 安全注意事項

- Gmail App Password 僅能放 `.env`，不可放 `.env.example` 真值。
- SMTP 密碼/API key/AWS 憑證不可提交 git。
- log 不可輸出 SMTP 密碼或 secret。
