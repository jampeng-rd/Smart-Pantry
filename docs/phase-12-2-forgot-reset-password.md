# Phase 12-2：Forgot Password / Reset Password

## 目標

實作 Account Recovery 的 forgot/reset password 流程，並維持既有分層架構與 email provider abstraction。

## 本階段完成內容

- 新增 Alembic migration：`migrations/versions/20260515_0010_password_reset_tokens.py`
- 新增資料表：`password_reset_tokens`
- 新增後端 API：
  - `POST /auth/forgot-password`
  - `POST /auth/reset-password`
- 新增前端頁面：
  - Forgot Password
  - Reset Password
- Login 頁新增「忘記密碼」入口
- forgot/reset 流程整合既有 email provider abstraction（`email_client_factory`）

## 資料庫變更

`password_reset_tokens` 欄位：

- `id`：PK
- `user_id`：FK -> `users.id`，index
- `token_hash`：`String(128)`，unique index
- `expires_at`：timezone-aware datetime，index
- `used_at`：timezone-aware datetime，可為 null
- `created_at`：timezone-aware datetime

安全規則：

- 只儲存 token hash，不儲存明文 token。
- reset token 過期、已使用、錯誤都視為無效。

## 後端行為

### POST /auth/forgot-password

- request: `{ "email": "user@example.com" }`
- 無論 email 是否存在，都回相同成功訊息。
- 若 email 存在：
  1. 建立一次性 reset token（明文僅用於寄信）
  2. DB 只存 token hash
  3. 透過既有 email client 寄送信件

### POST /auth/reset-password

- request: `{ "token": "...", "new_password": "..." }`
- token 無效 / 過期 / 已使用時回繁中友善錯誤。
- 成功時：
  1. 更新 `users.password_hash`
  2. 標記 `password_reset_tokens.used_at`
  3. 撤銷該使用者既有 refresh tokens

## 前端變更

- Auth flow 新增兩個 view：
  - `/forgot-password`
  - `/reset-password`
- Login 卡片新增忘記密碼入口。
- Forgot Password 成功訊息固定，不暴露 email 是否存在。
- Reset Password 顯示繁中友善錯誤，不顯示 raw exception/provider 細節。

## 測試

後端：`backend/tests/test_auth_service.py`

- forgot password 在 email 存在/不存在時回相同訊息
- reset token 僅儲存 hash
- reset token 過期回繁中友善錯誤
- reset token 已使用回繁中友善錯誤
- reset password 成功後既有 refresh token 失效

前端：

- `cd frontend && npm run build` 通過
- forgot/reset 頁面與型別編譯通過

## 驗收限制確認

- 未提前實作 Phase 12-3（deployment migration/rollback/failure handling）。
- 未修改 baseline migration。
- reset password 成功後會撤銷既有 refresh tokens。
