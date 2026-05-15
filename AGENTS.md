# Smart Pantry & Nutritionist 專案 Codex 工作規範

## 1. 專案定位

本專案正式中文名稱：**智慧食材保存與膳食管理系統**。英文名稱：**Smart Pantry & Nutritionist**。

本專案是全端 MVP，目標是建立智慧食材庫存、過期提醒、購物清單與 AI 膳食輔助系統。

核心順序：先完成人工手動輸入、庫存 CRUD、過期提醒、購物清單、繁體中文 Web UI，再逐步加入 AI 食譜推薦、食材照片辨識。餐點營養粗估（Nutrition）因單張照片估算份量與熱量精準度不足，暫不列入下一階段 MVP，後續僅在有使用者份量確認與生活參考聲明時再評估。

系統包含：`backend/` FastAPI、`frontend/` React + Vite + TypeScript + Redux Toolkit、PostgreSQL、Docker Compose、GitHub Actions、`docs/`、`agent-docs/`。

## 2. Codex 必須遵守的總規則

1. 每次任務開始前，先閱讀本檔案與 `agent-docs/`。
2. 後端必須分層：API Layer → Service Layer → Domain Layer → Infra Layer。
3. 不同功能必須分檔：auth、pantry、expiration、shopping、recipes、nutrition 不可混在同一 route/service。
4. 前端不同功能必須分 feature：auth、pantry、expiration、shopping、recipes、ingredients、profile、settings、help、theme；nutrition 暫緩時不可新增未完成 placeholder 功能。
5. 前端 UI 主要語言必須是繁體中文。
6. 前端按鈕需優先使用 `react-icons`；純 icon button 要有 `aria-label`；列表/導覽/選項使用「icon + 繁體中文」。
7. 前端必須支援柔和亮色與柔和暗色主題切換，不使用純白 `#ffffff` 或純黑 `#000000` 當主要背景。
8. Auth 必須使用 access token + refresh token；access token 快過期時前端自動 refresh，避免使用者突然被強制登出。
9. Python 函式、類別、重要方法都要有繁體中文 docstring。
10. TypeScript 公開函式、service、slice、重要工具函式要有繁體中文註解。
11. 後端每個功能都要有可單獨執行的單元測試。
12. 每階段完成後建立或更新 `docs/phase-xx-*.md`，並同步更新 README。
13. Python 套件只能安裝在 `.venv`，禁止全域安裝。
14. v1 資料庫必須使用 PostgreSQL，不用 SQLite 作主要資料庫。
15. 開發階段以本地 Docker PostgreSQL 為主；部署階段再使用 managed PostgreSQL。
16. AI 結果不可直接信任；涉及圖片辨識結果必須由使用者確認。
17. 餐點營養估算僅供生活參考，不可宣稱精準或專業營養診斷。
18. 文件需記錄效能與擴充性風險：DB 連線、pagination、索引、AI 任務延遲、背景任務、水平擴充。

## 3. 建議專案目錄

```text
backend/app/api/{health,auth,pantry,expiration,shopping,recipes,ingredients,nutrition}.py
backend/app/services/{auth_service,pantry_service,expiration_service,shopping_service,recipe_service,nutrition_service}.py
backend/app/domain/{schemas,models,enums}.py
backend/app/infra/{database,repository,settings,security,llm_client,storage}.py
ai_server/{app,workers,clients}
frontend/src/app/{store,hooks}.ts
frontend/src/features/{auth,pantry,expiration,shopping,recipes,ingredients,nutrition,theme}/
frontend/src/services/{apiClient,tokenService}.ts
frontend/src/styles/{theme.css,globals.css}
```

## 4. Auth 與 Token 規範

- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- 後端提供 `POST /auth/refresh` 與 `POST /auth/logout`。
- Refresh token 必須儲存在 DB 中的 `refresh_tokens`，且只儲存 token hash，不儲存明文 token。
- `refresh_tokens` 至少包含：`token_hash`、`user_id`、`expires_at`、`revoked_at`、`created_at`、`replaced_by_token_id`。
- Refresh token 必須支援 revoke / logout。
- 前端 MVP 可使用 `sessionStorage` 儲存 access token / refresh token。
- `sessionStorage` 關閉分頁後會清除，但仍有 XSS 風險，文件必須標示安全限制。
- 正式環境建議 refresh token 改用 `httpOnly secure cookie`。
- 前端 request 前檢查 access token 是否快過期；若快過期，先 refresh。
- 若 API 回傳 401，最多 refresh 一次並重送原 request。
- Refresh 失敗才清除登入狀態並導回登入頁。

### 4.3 前端 User-Scoped State Isolation（Critical）

- `recipes`、`ingredients`、`theme/settings` 屬於 user-scoped 前端狀態，必須以目前登入使用者為隔離邊界。
- 同一使用者在站內切頁再返回時，可保留其進行中的 recipes / ingredients 狀態。
- `logout`、切換帳號、auth 初始化失敗、token 失效導致登入狀態失效時，必須重置前一使用者的 user-scoped 狀態。
- 不可讓下一位登入者看到上一位使用者的 recipes 結果、ingredient preview/candidates、或 theme 偏好。
- `ingredients` 狀態清理不可採用「component unmount 一律清空」作為最終方案，需改以 auth/user identity 變更事件清理。

## 4.1 時間與時區策略

- 後端與 DB 一律使用 UTC timezone-aware datetime。
- API datetime 回傳必須帶 `Z` 或 `+00:00`。
- 不在後端儲存使用者本地時間（例如 Asia/Taipei、America/New_York）。
- 前端顯示時再依瀏覽器 timezone 或未來 `user_preferences.timezone` 轉換成本地時間。
- Phase 06 MVP 先使用瀏覽器 `Intl API` 顯示本地時間。

## 4.2 Forgot Password / Reset Password 安全規範

- 後端需提供 `POST /auth/forgot-password` 與 `POST /auth/reset-password`。
- forgot password API 不可暴露 email 是否存在；email 存在與不存在都回相同成功訊息。
- reset token 只存 hash，不存明文 token。
- reset token 過期、已使用、錯誤時，回傳繁體中文友善錯誤訊息。
- reset password 成功後必須：
  - 更新 `password_hash`
  - 標記 reset token `used_at`
  - revoke 該使用者既有 refresh tokens
- Forgot Password 寄信必須使用既有 email provider abstraction，不可建立獨立 forgot password SMTP implementation。
- 必須共用既有 `EMAIL_PROVIDER`、Gmail SMTP provider、Resend provider、`FakeEmailClient`、`email_client_factory`。

## 5. 圖片與檔案儲存規範

- 不可把圖片 blob 或 base64 直接存入 PostgreSQL。
- 開發階段可先將圖片存入本機 `uploads/` 目錄。
- PostgreSQL 只存 `image_path` 或 `image_url`。
- 上傳圖片大小限制預設為 5MB。
- 圖片上傳後可進行壓縮、resize 或格式轉換，以降低儲存與傳輸成本。
- 正式環境使用 object storage，例如 AWS S3、Cloudflare R2、MinIO 或相容服務。
- 食材辨識 / Vision 的候選結果可用 JSON / JSONB 儲存，但大型圖片內容不可放入 DB。

## 6. AI 效能規範

- `backend/` 是 Web API server，只負責 auth、pantry、expiration、shopping、AI job API、使用者驗證與資料權限，不可同步等待長時間 AI 推論。
- `ai_server/`（或 `ai_worker`）負責 LangChain、Ollama、Vision、Nutrition 等長任務執行；不作為一般使用者公開 API。
- frontend 不可直接呼叫 `ai_server/`，只能呼叫 `backend/`。
- API route 不可直接 import 或呼叫 LangChain / ChatOllama。
- AI 任務採 job-based：建立 job → 回傳 `job_id` → worker 處理 → 前端輪詢 backend job status。
- recipes / ingredient photo job 查詢 API 必須以 `user_id` 做資料隔離，不可跨使用者讀取任務狀態與結果。
- Phase 08-0～08-2 使用 PostgreSQL `ai_jobs` + DB polling worker。
- Phase 08～12 不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ；Expiration Email Reminder 在 Phase 08～12 一律使用 DB polling / scheduler worker 實作，
Phase 13 再評估 queue。
- 若任務量成長，再於 Phase 13 升級正式 queue（首選 RQ + Redis）。

### 6.1 Worker isolation 與 Ollama runtime 隔離差異

- `job_type` worker isolation 只隔離「DB claim 與 worker process」，不等於模型推論硬體隔離。
- 若 `OLLAMA_TEXT_BASE_URL` 與 `OLLAMA_VISION_BASE_URL` 未設定，兩者會 fallback 到 `OLLAMA_BASE_URL`，代表 text/vision 共用同一個 Ollama runtime。
- 即使分開啟動 recipe worker 與 ingredient worker，只要同一台機器共用 CPU/GPU/RAM/VRAM，Vision 推論仍可能拖慢 recipe latency。
- 本地若只用單一 runtime（例如 `http://localhost:11434`）屬於 MVP 可接受方案，但不代表已完成效能隔離。
- 可用不同 base URL 指向不同 Ollama instance（例如 `11434` 與 `11435`）先做 runtime 分流；若仍在同機同 GPU，仍可能互相影響。
- 真正降低互相影響需分開 GPU、分開機器，或提升硬體資源。

## 7. LangChain 與 AI 套件規範

- AI 階段使用 LangChain 1.x 系列。
- 建議使用：`langchain>=1.0,<2.0`、`langchain-core>=1.0,<2.0`、`langchain-ollama>=1.0,<2.0`。
- Codex 實作時需以當時 pip 可安裝且相容的版本為準。
- LLM client 可封裝於 `ai_server/clients/`（或過渡期封裝在 `backend/app/infra/llm_client.py`，但 route 不可直接呼叫）。
- API route 不可直接 import 或呼叫 LangChain / ChatOllama。
- Service 層只能依賴 protocol / interface，不可直接依賴 LangChain 類別。

## 8. 效能與穩定性規範

MVP 可先以單一 backend instance + 本地 Docker PostgreSQL 運作，但需保留擴充可能：

- 所有列表 API 必須支援 pagination。
- 查詢需使用 user_id 條件與必要索引。
- DB engine / session factory 集中管理，不可每次 request 重新建立 engine。
- 可水平擴充 backend。
- 部署階段 DB 使用 managed PostgreSQL。
- 可用 Redis cache 熱門 Dashboard summary。
- 加入 rate limit，避免大量請求造成服務阻塞。

## 9. 購物清單與庫存關係規範

- `pantry_items` 代表目前庫存。
- `shopping_list_items` 代表購物清單。
- `source_pantry_item_id` 只表示購物項目來源於某筆庫存項目，不代表自動更新庫存。
- `source_pantry_item_id` 為內部關聯欄位，不在 UI 顯示來源 ID。
- 標記 `is_purchased=true` 只記錄 `purchased_at`。
- 不可自動寫入 `pantry_items`。
- 若要把已購買項目加入庫存，必須由使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note` 後才可寫入。
- 已購買項目確認加入 pantry 成功後，前端可自動移除原 shopping item（使用既有 API 串接，不新增後端 API）。
- 未來可新增 convert-to-pantry API，但 request 必須明確提供上述欄位。

## 10. 前端 UI 架構與 Dashboard 規範

- Web UI 必須是一個完整系統，而不是單獨頁面集合。
- 未登入使用者進入網站時，首頁必須先顯示登入 / 註冊頁。
- 使用者登入成功後預設進入 Pantry（`/pantry`）。
- 註冊成功後預設進入 Pantry（`/pantry`）。
- 已登入使用者若進入首頁 `/`，自動導向 `/pantry`。
- Dashboard 採用「左側 Sidebar + 右側 Workspace」版型。
- `/dashboard` route 保留作為未來總覽頁，但 MVP Sidebar 導覽暫時隱藏「儀表板」項目。

### Sidebar 規範

Sidebar 需包含：

- 最上方 Logo。
- Logo 右側需有 Sidebar 收合按鈕（icon button）。
- 中間為功能導覽區（MVP 目前顯示）：Pantry、Expiration、Shopping、Recipes、食材辨識。Nutrition route 可保留但 Sidebar 先隱藏。
- Dashboard route 保留但導航先隱藏；Settings 由使用者選單進入。
- Phase 14-1 後可新增「會員管理」導航，但僅 admin 可見。
- 底部固定顯示目前登入使用者。

### 使用者選單規範

點擊 Sidebar 底部使用者區塊後：

- 需在側邊欄內向上展開使用者選單。
- 第一列顯示目前登入使用者。
- 下方至少包含：
  - Profile
  - Settings
  - Help
  - 升級 PRO（Phase 14 規劃，位置在 Help 下方、Log out 上方）
  - Log out

- 「升級 PRO」入口不放 Sidebar 主導航。
- 「升級 PRO」入口規劃放在 `frontend/components/layout/UserMenu.tsx`。
- 「登出」維持最後一個選項。

### Workspace 規範

- Dashboard 右側為主要工作區。
- Workspace 最上方需有當前頁面工具列（page toolbar / action bar）。
- Toolbar 可放搜尋、篩選、新增按鈕、排序等頁面功能。

## 11. 前端實作階段拆分

Phase 06 不可一次做完整前端。必須拆分子階段：

- Phase 06-1：Auth UI + App Layout
- Phase 06-2：Dashboard + Sidebar + Theme
- Phase 06-3：Pantry UI
- Phase 06-4：Expiration UI
- Phase 06-5：Shopping UI
- Phase 06-6：前端整合與 UX 修正

每個子階段都需：

- 可單獨測試
- 更新 docs
- 更新 README
- 維持 frontend build 可通過

## 12. Phase 12：Database Migration / Account Recovery

- Phase 12-0：文件與階段方向調整
- Phase 12-1：Alembic Migration System
- Phase 12-2：Forgot Password / Reset Password
- Phase 12-3：Deployment Migration / DB Upgrade 驗收(文件調整)

策略：

- 原本 Phase 12 AI Queue / Worker Scaling 順延到 Phase 13。
- 因現有資料表與 schema 持續增加，需先導入 Alembic 作為正式 schema 變更流程。
- 引入 migration 後，不可再以手動 `ALTER TABLE` 作為正式流程。
- Forgot Password 需要新增 `password_reset_tokens`，必須建立 migration 基礎後再實作。
- MVP / production deployment 未來需執行：`alembic upgrade head`。

## 13. AI 階段拆分與 Queue 策略（先規劃）

- Phase 08-0：AI Server / AI Job 架構初始化
- Phase 08-1：AI 食譜推薦 Mock（`ai_jobs` + fake worker，不呼叫真實 Ollama）
- Phase 08-2：AI 食譜推薦 LangChain + Ollama
- Phase 09：食材照片辨識（沿用 `ai_jobs`）
- Phase 13：AI Queue / Worker Scaling（視需求導入，首選 RQ + Redis）

策略：

- MVP 與目前 production deployment 持續使用 PostgreSQL `ai_jobs` + DB polling worker。
- Phase 13 目前只做文件規劃，不立即實作 queue migration。
- Phase 08～12 不將 RabbitMQ 作為預設方案。
- 僅在未來需要複雜 message routing、多服務事件流或更高階 broker 能力時，再評估 RabbitMQ。

## 14. Phase 14：Admin / Billing / Web Deployment（新主線）

- Phase 14-0：文件與架構方向調整
- Phase 14-1：Admin 權限與會員管理基礎
- Phase 14-2：Web Deployment Baseline（Render + Vercel）
- Phase 14-3：Billing 核心資料模型與 Upgrade 入口
- Phase 14-4：藍新單次付款（one-time）
- Phase 14-5：藍新訂閱制（subscription）
- Phase 14-6：Admin Billing Management

規劃重點：

- admin 權限最終需由 DB 欄位控制（`role` 或 `is_admin`），不可只做前端判斷。
- backend admin API 不混入既有 `backend/app/api/`，改為獨立資料夾（例如 `backend/app/admin_api/`），但仍維持分層架構。
- 既有帳號 `jampeng.rd@gmail.com` 規劃為第一個 admin 帳號來源之一。
- 空 DB 初始部署需有第一個 admin 建立方案（migration seed / init script / bootstrap command / 手動 SQL / 後台初始化流程），Phase 14-0 僅文件規劃，不先實作 runtime。
- Billing 統一入口：`/billing/upgrade`，並依 `BILLING_MODE=one_time|subscription` 導向 `/billing/newebpay-one-time` 或 `/billing/newebpay-subscription`。
- 單次付款與訂閱制為不同制度，但需共用部分 billing 資料模型。
- Web 先部署 backend(Render) + frontend(Vercel)；AI server / Ollama 暫不列入本輪部署。
- 金流 callback / notify 需要公開網址，因此 Web Deployment 需先完成。

## 12.1 AI 功能階段完成門檻（Phase 08～12）

Phase 08～12 每一個 AI 功能都必須以前後端完整可操作為完成標準，不可只完成 backend API、ai_worker 或文件後就進下一階段。Phase 10 已改為 Profile / Settings / Help / Email Reminder，不再視為 AI Nutrition 階段。

每個 AI 功能階段至少需包含：

1. backend job API：建立 job、查詢 job status/result，並驗證 user_id 權限。
2. ai_worker：claim pending job、執行 AI/mock、寫回 success/failed。
3. frontend feature UI：建立 job、輪詢 job、顯示 pending/running/success/failed。
4. 使用者確認流程：AI/Vision 候選資料不可直接寫入正式資料。
5. 測試：backend 單元測試、fake worker 測試、frontend build。
6. 文件：更新 docs/phase-xx-*.md 與 README。
7. 手動整合驗收：backend + frontend + ai_worker + Ollama 可完整操作。
8. 通過上述驗收後，才能進入下一個 Phase。

### Phase 08：AI 食譜推薦完整功能

- Phase 08-0：AI Server / AI Job 架構初始化
- Phase 08-1：AI 食譜推薦 Mock Worker
- Phase 08-2：AI 食譜推薦 LangChain + Ollama
- Phase 08-3：Recipes 前端 UI 串接

### Phase 09：食材照片辨識完整功能

- Phase 09-1：Ingredient Photo Job API + Mock Worker
- Phase 09-2：Vision Model 候選食材辨識
- Phase 09-3：Ingredient Photo 前端 UI + 使用者確認寫入 Pantry

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ

### Phase 10：Profile / Settings / Help / Expiration Email Reminder

Nutrition 暫緩，不在下一階段實作。Phase 10 改為補齊使用者設定、系統設定、說明頁與到期 Email 提醒。

- Phase 10-0：文件與階段方向調整
- Phase 10-1：Profile / Settings / Help 前端與偏好資料模型
- Phase 10-2：Expiration Email Reminder 後端排程與寄信服務
- Phase 10-3：Expiration Email Reminder 前端設定與寄送紀錄

### Phase 11：Email Provider / Scheduler / Reliability

- Phase 11-0：Email Provider 策略與文件調整
- Phase 11-1：Gmail SMTP 真實寄信（開發/測試/個人或工作室帳號）
- Phase 11-2：Production Email Provider（Resend / SendGrid / Amazon SES）
- Phase 11-3：正式 scheduler / cron / docker deployment
- Phase 11-4：retry / failure handling / monitoring

## 14. Phase 10：Profile / Settings / Help / Expiration Email Reminder 規範

Phase 10 不做 Nutrition。理由是單張餐點照片難以準確推估份量、油量、醬料與食材比例，若直接宣稱熱量或營養估算容易造成誤導。後續若恢復 Nutrition，必須加入使用者確認份量與明確生活參考聲明。

### Profile（個人資料）

Profile 只處理帳號與個人基本資料：

- 使用者名稱（可修改）。
- Email（不可修改，作為登入與通知識別）。
- 頭像：若未上傳圖片，使用 display_name 第一個字元作為預設頭像，例如 `YG` 顯示 `Y`，`小明` 顯示 `小`。
- 修改密碼。

### Settings（系統設定）

Settings 處理系統行為與偏好，主題切換需放在第一個區塊：

1. 外觀設定：主題切換（柔和亮色 / 柔和暗色；未來可加跟隨系統）。
2. 到期 Email 提醒設定：選項順序必須是「不提醒」、「前 1 天（預設）」、「前 3 天」。
3. 時區：預設可使用瀏覽器時區，後續可讓使用者選擇，例如 `Asia/Taipei`。
4. 語言：MVP 固定繁體中文，先保留欄位與文件說明。
5. 登出所有裝置：未來功能。
6. 最近登入時間：未來功能。

### 到期 Email Reminder 規則

- 提醒設定建議放在 `user_preferences` 或獨立一對一偏好表，不建議直接塞滿 `users` auth 表。
- 建議欄位：`expiration_email_reminder_days`，允許值：`none`、`1`、`3`，預設 `1`。
- 寄送時間固定為每天上午 8:00 與下午 5:00。
- 同一使用者同一天同一批即將到期商品最多寄送兩次（上午一次、下午一次）。
- 需建立 reminder log / delivery log 以避免同一時段重複寄送。
- 系統每天在固定時間檢查每位使用者設定與 pantry expiration_date，符合條件才寄送。
- Email provider 可能產生成本；MVP 可使用有免費額度的 provider，但正式環境需記錄發信量與失敗重試。

### Email Provider 階段規範（Phase 11）

- `fake`：預設模式，不寄真信。
- `gmail_smtp`：僅建議開發/測試/少量寄送，不建議正式大量寄送。
- `production provider`：正式環境建議使用（Resend / SendGrid / Amazon SES）。
- 單元測試不可寄真信，必須使用 fake/stub email client。
- 所有 secret（SMTP 密碼、API key、AWS 憑證）不可提交到 git。
- Gmail app password 只能放在 `.env`，不可在 `.env.example` 放真值。

### Help（說明）

Help 頁面需提供：

- 食材庫存、到期提醒、購物清單基本使用教學。
- 食譜建議與食材辨識的使用限制。
- 食材照片辨識建議：單一或少量食材、避免整桌料理/冰箱全景/模糊照片。
- 到期 Email 提醒規則：提醒選項、每日 8:00 / 17:00、每天最多兩次。
- FAQ：AI 結果不準、食譜重複、Email 沒收到、如何修改提醒設定。
