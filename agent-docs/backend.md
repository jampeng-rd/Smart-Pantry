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
- Phase 09～11：若延遲可接受，持續沿用 DB polling worker。
- Phase 12：任務量明顯增加時，升級為 RQ + Redis（首選）；Dramatiq + Redis 為備選。
- RabbitMQ 非 MVP 與 Phase 08～11 預設方案，僅在複雜 routing/事件流需求時評估。
- DB engine / session factory 集中管理，不可每次 request 重新建立 engine。

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
  - 結尾需包含：`此信件來自【智慧食材保存與膳食管理系統】自動發送，無需回覆 謝謝您。`
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
