# 後端架構規範

## 技術棧

Python 3.10+、FastAPI、Pydantic v2、pydantic-settings、pytest、httpx、PostgreSQL、SQLAlchemy 2.x、Docker、passlib/bcrypt 或 argon2、PyJWT / python-jose。

AI 階段使用 LangChain 1.x 系列，建議：

```text
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langchain-ollama>=1.0,<2.0
```

實際版本需以當時 pip 可安裝且相容為準。

## 分層責任

## Server 分工

- `backend/`：Web API server。負責 auth、pantry、expiration、shopping、AI job API、使用者驗證、資料權限。
- `ai_server/`（或 `ai_worker`）：AI runtime/worker。負責 LangChain、Ollama、Vision、Nutrition 長任務。
- frontend 不直接呼叫 `ai_server/`，只呼叫 `backend/`。
- `ai_server/` 不作為一般使用者公開 API。
- backend 不可同步等待長時間 AI 推論。
- API route 不可直接呼叫 LangChain / ChatOllama。

### API Layer

`backend/app/api/` 只接收 request、驗證 schema、呼叫 service、回傳 response、管理 dependency。禁止直接操作 DB、直接呼叫 LLM、直接寫商業邏輯。

### Service Layer

`backend/app/services/` 處理 auth、refresh token、食材 CRUD、過期判斷、購物清單、AI 食譜、營養粗估。

### Domain Layer

`backend/app/domain/` 定義 Pydantic schema、SQLAlchemy model、enum、統一 response 格式。

### Infra Layer

`backend/app/infra/` 處理 DB、repository、settings、JWT/password hash、refresh token 儲存、LLM client、OCR client、檔案儲存。

## 建議目錄

```text
backend/app/api/{health,auth,pantry,expiration,shopping,recipes,ingredients,nutrition}.py
backend/app/admin_api/{auth,members,billing}.py
backend/app/services/{auth_service,pantry_service,expiration_service,shopping_service,recipe_service,ingredient_service,nutrition_service}.py
backend/app/domain/{schemas,models,enums}.py
backend/app/infra/{database,repository,settings,security,llm_client,ingredient_client,storage}.py
```

## Auth 設計要求

- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- refresh token 儲存在 DB，只存 token hash，不存明文 token。
- refresh token 必須支援撤銷與 logout。
- `refresh_tokens` 儲存 token_hash、user_id、expires_at、revoked_at、created_at、replaced_by_token_id。
- 前端自動 refresh 時，後端回傳新 access token；若採 rotation，也回傳新 refresh token。
- MVP 前端可使用 sessionStorage 儲存 token，但文件需標示 XSS 風險。
- 正式環境建議 refresh token 改用 httpOnly secure cookie。

## 圖片與檔案上傳要求

- 不把圖片 blob / base64 存 PostgreSQL。
- 開發階段可先存本機 `uploads/`。
- DB 只存 image_path / image_url。
- 上傳圖片大小限制預設 5MB。
- 可在上傳後壓縮、resize 或轉成較適合的格式。
- 正式環境使用 S3 / R2 / MinIO 等 object storage。

## 效能要求

- Repository 查詢不可一次讀取所有使用者資料。
- 列表 API 必須支援 page / page_size。
- Dashboard summary 避免 N+1 query。
- AI/OCR/Vision 在 worker 內可同步呼叫模型，但 backend request 不可同步等待 AI 任務完成。
- Phase 08-0～08-2：使用 PostgreSQL `ai_jobs` + DB polling worker（非 Redis queue）。
- Phase 09～12：一律沿用 PostgreSQL `ai_jobs` + DB polling worker。
- recipes 與 ingredient photo job status API 必須以 `user_id` 隔離，禁止跨使用者讀取任務結果。
- Phase 13 統一評估並導入 RQ + Redis（視任務量需求）
- RabbitMQ 非 MVP 與 Phase 08～12 預設方案，僅在複雜 routing/事件流需求時評估。
- DB engine / session factory 集中管理，不可每次 request 重新建立 engine。

## Phase 12：Database Migration / Account Recovery 後端規範

### Phase 12-1：Alembic Migration System

- 導入 Alembic，建立 `alembic.ini`、`migrations/`，並連接既有 SQLAlchemy metadata。
- 建立 baseline migration 對齊現況資料表。
- 後續 schema 變更（新增欄位、索引、資料表）必須透過 migration。
- 不可再以手動 `ALTER TABLE` 作為正式流程。

### Phase 12-2：Forgot Password / Reset Password

- 新增 `POST /auth/forgot-password`、`POST /auth/reset-password`。
- `password_reset_tokens` 僅儲存 `token_hash`，不可儲存明文 token。
- forgot password API 不可暴露 email 是否存在，email 存在/不存在都回相同成功訊息。
- reset token 過期、已使用、錯誤時回繁中友善錯誤。
- reset password 成功後需：
  - 更新 `password_hash`
  - 標記 reset token `used_at`
  - revoke 該使用者既有 refresh tokens

Forgot Password 寄信實作限制：

- 必須共用既有 email provider abstraction，不可直接綁定 Resend/Gmail。
- 不可建立獨立 forgot password SMTP sender。
- 必須共用既有 `EMAIL_PROVIDER`、Gmail SMTP provider、Resend provider、`FakeEmailClient`、`email_client_factory`。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ

補充：

- worker 分開只代表 job claim/process 分流，不等於 Ollama runtime 或硬體資源隔離。
- `OLLAMA_TEXT_BASE_URL` / `OLLAMA_VISION_BASE_URL` 未設定時會 fallback 到 `OLLAMA_BASE_URL`，text/vision 仍共用同一 runtime。
- 同機部署下若共用 CPU/GPU/RAM/VRAM，Vision 推論仍可能影響 recipe latency。
- 若要降低影響，至少拆分不同 runtime URL；若要明顯改善，需分開 GPU 或分開機器。


## Phase 10：Profile / Settings / Help / Expiration Email Reminder 後端規範

Nutrition 暫緩。Phase 10 後端重點改為使用者偏好、設定與到期 Email 提醒。

### Profile API

- 取得目前使用者 profile。
- 更新使用者名稱。
- Email 不可修改。
- 修改密碼需驗證目前密碼。
- 若沒有頭像圖片，前端以 display_name 第一個字元產生預設頭像；後端可暫不儲存 avatar。

### Settings / Preferences API

- 儲存主題、時區、語言、到期 Email 提醒設定。
- 到期提醒選項順序：不提醒、前 1 天（預設）、前 3 天。
- 建議存在 `user_preferences`，不要直接塞在 `users` auth 表。

### Expiration Email Reminder

- 每天固定上午 8:00 與下午 5:00 執行檢查。
- 依每位使用者 `expiration_email_reminder_days` 找出符合到期提醒的 pantry items。
- 同一天同一使用者最多寄送兩次：上午一次、下午一次。
- 需有 delivery log 避免重複寄送。
- Email provider 需封裝於 infra，例如 `email_client.py`，service 不直接綁特定 provider。
- MVP 可先提供 fake email client / log email client 測試，不可在單元測試寄真信。
- MVP 到期提醒信需提供純文字 fallback，並可附 HTML table：
  - subject：`【智慧食材保存系統】食材即將到期提醒`
  - body 應包含：使用者名稱、設定的到期日、`食材名稱/數量/單位/保存位置`
  - `保存位置` 空值顯示 `未設定`
  - 結尾需包含：`此信件由系統自動發送，無需回覆。`
  - HTML 版本建議使用 inline style，不依賴外部 CSS 與圖片。

## Phase 11：Email Provider / Scheduler / Reliability 後端規劃

### Phase 11-0：Email Provider 策略與文件調整

- 明確定義 `fake` / `gmail_smtp` / `production` 三種 provider 模式。
- `.env.example` 只保留鍵名與範例，不放任何真實 secret。

### Phase 11-1：Gmail SMTP 真實寄信

- 目標：支援開發/測試/個人或工作室帳號真實寄送。
- 限制：僅適合少量寄送，不建議正式大量使用。
- 安全：Gmail app password 只能存在 `.env`，不可提交 git。
- 實作：以 `smtplib + email.message.EmailMessage + STARTTLS(587)` 封裝於 infra email client。
- service 層僅依賴 `BaseEmailClient`，不可直接依賴 Gmail 細節。

### Phase 11-2：Production Email Provider

- 正式環境建議使用 Resend / SendGrid / Amazon SES。
- service 層維持 provider abstraction，不直接綁定單一廠商 SDK。
- Phase 11-2 僅實作 Resend；SendGrid / SES 僅保留設定鍵與錯誤訊息，避免假成功。
- `EMAIL_PROVIDER=production` 時需有 `EMAIL_FROM_ADDRESS`。
- `PRODUCTION_EMAIL_PROVIDER=resend` 時需有 `RESEND_API_KEY`。

### Phase 11-3：正式 scheduler / cron / docker deployment

- 將目前手動 runner 轉為正式排程（scheduler / cron / container deployment）。
- 需保留上午 8:00、下午 5:00 的寄送策略與 delivery log 去重機制。

### Phase 11-4：retry / failure handling / monitoring

- 補齊失敗重試、退避策略、可觀測性（log/metrics/告警）與寄送失敗追蹤。
- 需可區分 provider error、網路錯誤與無效收件地址類型。

## Phase 11-3 Runner 規範

`backend/app/jobs/expiration_email_runner.py` 必須支援：

- 不帶 `--send-window` 自動判斷：08 => `morning_08`，17 => `evening_17`
- 非排程時段可明確略過，不執行寄送流程
- `--send-window` 可覆蓋自動判斷
- `--scheduled-date YYYY-MM-DD` 指定業務日期
- 錯誤時回傳非 0 exit code

時區策略：

- `SCHEDULER_TIMEZONE`（MVP 預設 `Asia/Taipei`）決定排程判斷時區
- DB datetime 仍為 UTC timezone-aware
- `scheduled_date` 為業務日期（配合 send_window 去重）

## Phase 11-4：Retry / Failure Handling / Monitoring

到期提醒服務新增 reliability 規範：

- `EMAIL_RETRY_MAX_ATTEMPTS`：預設 1，允許 0~3
- retry 僅限：timeout / network_error / provider_5xx
- 不可 retry：provider_4xx / invalid_configuration
- 固定 backoff：5s / 15s / 30s
- delivery log 需記錄：`attempt_count`、`last_error_message`、`last_attempt_at`、`final_status`
- `final_status`：`success` / `failed` / `permanent_failed`

安全要求：

- structured log 不可輸出 API key、Authorization header、SMTP password、secret

## Phase 11-4 User-facing Error Mapping 規範

- 後端保留完整 delivery 錯誤細節（`last_error_message`、`error_category`、structured logs）。
- 提供給一般使用者的 API 需回傳 `user_friendly_error_message`，不可直接暴露 provider 原始錯誤內容。
- 錯誤分類映射：
  - temporary：`timeout` / `provider_5xx` / retry 中
  - permanent：`provider_4xx` / `invalid_configuration` / 不可 retry
- user API 回應不可洩漏 API key、provider 詳細 exception、traceback。

## Phase 11-4 錯誤映射修正

後端 `user_friendly_error_message` 需區分四類：

1. 使用者 Email 無法寄送
2. 信件服務暫時不可用
3. 前端網路異常（由前端 API client 統一處理）
4. 系統設定或伺服器異常

`invalid_configuration`（如 API key invalid / domain not verified / invalid from）屬於系統設定異常，不得映射為使用者 Email 問題。

同時保留完整錯誤於 backend delivery log（`last_error_message`、`error_category`）與 structured logs，供 admin/monitoring 使用。

## Phase 11-4 Recipient/From 錯誤分類補充

- `invalid to` / `invalid recipient` / recipient email 格式錯誤（含不完整 domain/TLD） => 使用者 Email 無法寄送
- `invalid from` / `invalid sender` / API key invalid / domain not verified => 系統設定或伺服器異常
- backend user-facing mapping 必須明確區分 `to` 與 `from`，避免誤導使用者。

## Phase 14（規劃）：Admin / Billing / Web Deployment 後端方向

- Admin API 不混入既有 `backend/app/api/`，改放 `backend/app/admin_api/`。
- admin 權限判斷不可只在前端，最終必須由 DB 欄位與後端權限驗證控制（例如 `users.role` 或 `users.is_admin`）。
- `jampeng.rd@gmail.com` 需作為第一個既有 admin 帳號來源之一（實際寫入方式於 Phase 14-1 實作）。
- 若為空 DB 初始部署，第一個 admin 建立方式可採：migration seed、bootstrap command、init script、手動 SQL（皆需文件化）；Phase 14-0 僅規劃不實作。
- Billing 路由規劃：
  - `/billing/upgrade`
  - `/billing/newebpay-one-time`
  - `/billing/newebpay-subscription`
- `BILLING_MODE=one_time|subscription` 由後端設定決定 upgrade 入口導向策略（Phase 14-3+ 實作）。

## Phase 14-3：Billing 核心資料模型與 Upgrade 入口

- 新增 `backend/app/api/billing.py`：`GET /billing/upgrade`。
- 新增 `backend/app/services/billing_service.py`、`backend/app/infra/repository/billing_repository.py`。
- 新增 schema：`backend/app/domain/schemas/billing_schema.py`。
- 新增 model：
  - `billing_memberships`
  - `billing_transactions`
  - `billing_webhook_events`
- `BILLING_MODE=one_time|subscription` 由 backend settings 控制入口導向。
- 本階段僅建立基礎資料模型與入口，不包含真實金流扣款流程。

## Phase 14-4：NewebPay one-time 後端規範

- 新增 checkout service（不可把金流邏輯寫在 route）。
- checkout 需建立 `billing_transactions` 初始紀錄並回傳藍新表單欄位。
- notify 需驗證 `TradeSha`、解密 `TradeInfo`、更新 transaction/membership。
- return endpoint 需由 backend 接收（`POST /billing/newebpay/return`），再 redirect 到前端結果頁。
- webhook/callback 原始資料需保存到 `billing_webhook_events`。
- idempotency 以 `external_trade_no`（MerchantOrderNo）+ 成功狀態防護重送通知。
- 單次付款成功時啟用 PRO（MVP 規則：永久有效，`ended_at=null`）。
