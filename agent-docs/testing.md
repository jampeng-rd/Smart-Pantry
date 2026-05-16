# 測試規範

## 後端測試

後端每個功能都必須有單元測試，放在 `backend/tests/`。

## 必測功能

- health API。
- auth service：註冊、登入、密碼錯誤。
- refresh token：refresh 成功、過期、revoke / logout、無效 token。
- pantry service：新增、編輯、刪除、查詢、pagination。
- expiration service：即將過期、已過期。
- shopping service：新增、標記已購買、刪除。
- recipe service：prompt 組裝與 LLM mock。
- ingredient photo service：Vision mock 與候選資料整理
- nutrition service：粗估結果 parsing 與聲明。

## LLM / Vision 測試

不可在單元測試直接呼叫真實 Ollama。使用 fake client / stub client。

## Email Provider 測試原則（Phase 11）

- 單元測試不可寄真信。
- Email reminder 測試必須使用 fake/stub email client。
- 不可在 CI 使用 Gmail SMTP 或 Production provider 真實憑證。
- `.env.example` 只放欄位，不放真值；測試 secret 由 CI secret 管理。
- Gmail SMTP client 單元測試需以 stub/mock SMTP server 驗證，不可真實連線 Gmail。
- Resend client 單元測試必須 mock/stub HTTP client，不可真的呼叫 Resend API。
- production provider 測試至少覆蓋 `resend` 成功路徑、缺少必要設定、`sendgrid/ses` 尚未實作錯誤與不支援 provider 錯誤。

AI job 測試原則（Phase 08～12）：

- 不可在單元測試中呼叫真實 Ollama。
- 使用 fake AI client / fake worker。
- 測試 job 建立。
- 測試狀態轉換：`pending -> running -> success`。
- 測試 `failed` 狀態與 `error_message`。
- 測試跨使用者不可查詢 job。
- 測試 worker 不處理其他使用者不相干資料（僅處理被 claim 的 pending job）。
- recipe recommendation 需測兩種模式：
  - `selected_items`：建立成功、空陣列錯誤、跨使用者 pantry item 驗證失敗
  - `auto_from_pantry`：可建立 pending job，且 input snapshot 記錄 recommendation_mode

## API 測試

使用 FastAPI TestClient 或 httpx。測試成功與失敗案例，並確認 response 格式符合 `agent-docs/api.md`。

時間欄位需額外驗證：

- 新建立資料的 datetime 回傳需包含時區（`Z` 或 `+00:00`）。
- `purchased_at` 在 `is_purchased=true` 時需包含時區；`is_purchased=false` 時為 `null`。
- 後端與 DB 使用 UTC timezone-aware datetime，避免 naive datetime。

## Web 測試

v1 可先做 TypeScript 型別檢查、npm build、核心 utility function 測試、theme 切換 utility、tokenService refresh 行為測試。

```bash
cd frontend
npm run build
```

- Phase 06 MVP 需驗證使用瀏覽器 `Intl API` 將 UTC datetime 轉成本地時間顯示。
- 若後續加入 `user_preferences.timezone`，需驗證可覆蓋瀏覽器時區。

前端 user-scoped state isolation 測試補充：

- Recipes：
  - 使用者 A 產生 recipe result 後登出，使用者 B 登入不可看到 A 的 `result/jobStatus/polling/currentJobId`。
  - 同一使用者切到其他頁再回 `/recipes`，既有 job/result 狀態可保留，不應被誤清空。
- Ingredients：
  - 使用者 A 上傳圖片並出現 preview/candidates 後登出，使用者 B 登入不可看到 A 的 preview/檔名/候選表單/job 狀態。
  - 同一使用者切到其他頁再回 `/ingredients`，既有 preview/candidates/job 狀態可保留，不應被誤清空。
- Theme：
  - 使用者 A 變更主題後登出，使用者 B 登入應顯示 B 自己的 theme 偏好，不可沿用 A 的有效偏好。

## Token 與儲存測試補充

- refresh token 必須測試 hash 儲存，不可儲存明文 token。
- 測試 access token 過期後可透過 refresh token 取得新 access token。
- 測試 logout / revoke 後 refresh token 不可再使用。
- 前端 tokenService 需測試 sessionStorage 儲存、快過期 refresh、401 後最多重試一次。
- 驗證 `logout` / 切換帳號 / auth 初始化失敗後，recipes 與 ingredients 的 user-scoped state 會被 reset。

## 圖片與 Background Job 測試補充

- 圖片上傳需測試超過 5MB 時拒絕。
- 測試 DB 僅保存 image_path / image_url，不保存圖片 blob/base64。
- Phase 08～12 以 job-based 為主：需測 job 建立、狀態查詢、成功與失敗案例。
- Phase 13 若導入 RQ + Redis，需補測 enqueue、worker process、retry、失敗重試策略。

## Shopping 與 Pantry 關係測試補充

- 測試 `source_pantry_item_id` 僅做來源關聯，不會自動更新 pantry。
- 測試標記 `is_purchased=true` 只更新 shopping item 狀態與 `purchased_at`。
- 若未來新增 convert-to-pantry API，需測必填欄位確認流程（`name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`）。

## Phase 08～12 全端驗收要求

Backend / Worker：

- job 建立
- pending -> running -> success
- failed + 中文 error_message
- user_id 權限隔離
- fake worker / fake AI client 測試

Frontend：

- npm run build
- 可建立 job
- 顯示 pending/running/success/failed
- 停止 polling
- 中文友善錯誤
- 不直連 ai_server

Manual E2E：

- backend + frontend + ai_worker + Ollama 啟動
- 成功流程驗證
- 失敗流程驗證

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ


## Phase 10 Profile / Settings / Email Reminder 測試補充（10-1/10-2/10-3）

Backend：

- 測試 profile 取得與更新 display_name。
- 測試 email 不可修改。
- 測試修改密碼：目前密碼錯誤、新密碼成功。
- 測試 settings 取得與更新：theme、timezone、language、expiration_email_reminder_days。
- 測試 expiration_email_reminder_days 只允許 `none`、`1`、`3`，預設為 `1`。
- reminder worker、8:00/17:00 寄送與 delivery log 去重測試在 Phase 10-2。
- 測試 `GET /settings/expiration-reminder-deliveries`：
  - 未登入回 401。
  - 只能查自己的 delivery logs。
  - pagination 正確。
  - 最新紀錄在前。
  - `item_count` 依 `item_ids` 計算。
  - `failed` 回傳 `error_message`。
  - datetime 含 timezone。
- 測試 cleanup 保留規則：
  - `morning_08` 會清除超過 7 天 delivery logs。
  - `morning_08` 不會清除 7 天內紀錄。
  - `evening_17` 不執行 cleanup。
  - cleanup 不影響當天新產生的 delivery logs。

Frontend：

- Profile 顯示 Email 不可修改。
- 沒有頭像時顯示 display_name 第一個字元。
- Settings 第一個區塊是主題切換。
- 到期提醒選項順序：不提醒、前 1 天（預設）、前 3 天。
- Settings「最近寄送紀錄」有 loading / error+重試 / empty / pagination（使用共用 Pagination）。
- 手機版寄送紀錄為 card-like 顯示，避免表格過度橫向捲動。
- Help 頁顯示食材辨識、食譜建議與 Email 提醒說明。

## Phase 11-3 Scheduler 測試補充

至少覆蓋 runner 測試：

1. 不帶 send-window 可判斷 `morning_08`
2. 不帶 send-window 可判斷 `evening_17`
3. 非排程時段可明確略過
4. CLI 指定 send-window 可覆蓋自動判斷
5. 可指定 scheduled-date
6. service 例外時 exit code 非 0
7. 既有 fake / gmail_smtp / resend 測試持續通過

本階段不做 retry/monitoring 測試（留到 Phase 11-4）。

## Phase 11-4 測試補充

至少覆蓋：

1. `EMAIL_RETRY_MAX_ATTEMPTS` 預設值為 1
2. `EMAIL_RETRY_MAX_ATTEMPTS` 可由 env 覆寫
3. `EMAIL_RETRY_MAX_ATTEMPTS` 超過 3 應失敗
4. `EMAIL_RETRY_MAX_ATTEMPTS=0` 不 retry
5. `provider_5xx` / `timeout` / `network_error` 會 retry
6. `provider_4xx` / `invalid_configuration` 不 retry
7. retry backoff：5s / 15s / 30s
8. 超過最大次數進入 `permanent_failed`
9. runner summary 應有 `retry_count`、`permanent_failed_count`
10. log 不可包含 secret
11. resend/smtp timeout 設定存在（30s）

## Phase 12-1/12-2 測試補充（Migration + Account Recovery）

Alembic：

- migration 可建立與可執行（至少驗證 `upgrade head` 可跑）。
- 新增欄位/資料表必須有對應 migration 檔案。

Forgot Password / Reset Password：

- forgot password 在 email 存在/不存在時都回相同成功訊息。
- reset token 僅儲存 hash，不可儲存明文 token。
- reset token 過期時回中文友善錯誤。
- reset token 已使用時回中文友善錯誤。
- reset password 成功後，既有 refresh token 必須失效。
- CI / automated tests 禁止寄送真實 forgot password email。
- forgot password 測試必須使用 fake/stub email client。
- local manual testing 可使用 Gmail SMTP / Resend 驗證 email flow。

## Phase 12-3 測試與驗收補充（Deployment Migration / DB Upgrade）

至少補齊下列驗收：

1. `alembic upgrade head` 可在本地開發 DB 成功執行。
2. `alembic current` 可驗證目前 revision 已到 head。
3. migration 故障演練時，部署流程必須中止（staging/prod）。
4. production 升級驗收文件需包含 backup/snapshot 與 rollback 路徑。
5. 不可用 drop/recreate DB 取代正式升級流程。

## Phase 14-0 測試與驗收補充（文件與架構方向調整）

- 本階段不做 runtime 功能測試，重點為文件一致性驗收。
- 至少確認：
  1. Phase 14-0～14-6 子階段規劃文件完整。
  2. Phase 13 定位仍保留為 AI Queue / Worker Scaling（先規劃，暫不實作）。
  3. Admin 權限規範明確要求 DB 欄位控制，不可只靠前端判斷。
  4. Billing 入口與 `BILLING_MODE=one_time|subscription` 規範已文件化。
  5. Render + Vercel 部署邊界與 AI server 暫不部署範圍已明確記錄。

## Phase 14-2 測試與驗收補充（Web Deployment Baseline）

deployment smoke test 至少覆蓋：

1. backend `GET /health` 回 200
2. frontend 頁面可載入
3. login 可用
4. `/pantry`、`/shopping`、`/settings` 可進入
5. admin 帳號可進入 `/admin/members`
6. frontend API 請求確實打到 Render backend（`VITE_API_BASE_URL` 正確）
7. CORS 設定正確（允許 Vercel 網域、阻擋非 allowlist）
8. migration revision 驗證：`alembic current` 已到 head

migration 驗收強制規則：

- 雲端部署也必須執行 `alembic upgrade head`
- migration failure 必須中止 deployment
- production 不可使用 drop/recreate DB

## Phase 14-3 測試補充（Billing Core + Upgrade Entry）

Backend：
1. `BILLING_MODE=one_time` 時，`GET /billing/upgrade` 回傳單次付款入口。
2. `BILLING_MODE=subscription` 時，`GET /billing/upgrade` 回傳訂閱入口。
3. membership 存在且 `tier=PRO` + `membership_status=active/trialing` 時，`is_pro=true`。
4. 設定驗證：`BILLING_MODE` 僅允許 `one_time`、`subscription`。
5. migration 檔案存在且可在 DB 可用時執行 `alembic upgrade head`。

Frontend：
1. `/billing/upgrade` 可進入。
2. UserMenu「升級 PRO」可導到 `/billing/upgrade`。
3. `/billing/newebpay-one-time` 與 `/billing/newebpay-subscription` 目前為占位頁，不顯示成功付款。
4. `npm run build` 必須通過。

## Phase 14-4 測試補充（NewebPay one-time）

Backend：
1. `POST /billing/newebpay/one-time/checkout` 可建立 pending 交易並回傳藍新表單欄位。
2. `POST /billing/newebpay/notify` 成功通知會更新交易為 success 並啟用 PRO。
3. 同一成功通知重送不會重複升級（idempotency）。
4. 失敗通知不會升級 PRO，交易應為 failed。
5. webhook 原始資料會寫入 `billing_webhook_events`。

Frontend：
1. `/billing/newebpay-one-time` 可發起 checkout 並 form POST 至藍新測試 gateway。
2. `/billing/newebpay-one-time/result` 可查詢並顯示 success/failed/pending。
3. `npm run build` 必須通過。
