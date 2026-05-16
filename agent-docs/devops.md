# DevOps、PR 與 CI/CD 規範

## 目標

```text
feature branch → PR → CI → merge → CD
```

## PR 流程

建立 feature branch → 完成功能 → 補測試 → 階段文件 → README → 本地測試 → push → PR → CI 通過 → merge → 部署平台自動部署。

## 分支命名

```text
feature/phase-01-project-init
feature/phase-02-auth-refresh-token
feature/phase-03-pantry-crud
feature/phase-04-expiration-status
feature/phase-05-shopping-list
feature/phase-06-web-ui-theme
feature/phase-07-ci-cd
feature/phase-08-0-ai-job-architecture
feature/phase-08-1-ai-recipes-mock
feature/phase-08-2-ai-recipes-ollama
feature/phase-09-ingredient-photo
feature/phase-10-nutrition-estimate
feature/phase-12-db-migration-account-recovery
feature/phase-13-ai-queue-worker-scaling
```

## 最小 CI

```yaml
name: CI
on:
  push:
    branches: [master]
  pull_request:
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      - run: pytest backend/tests -q
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: |
          cd frontend
          npm ci
          npm run build
```

## 部署規劃

- Backend：Render / Railway / AWS EC2。
- Frontend：Vercel / Netlify。
- 開發 DB：本地 Docker PostgreSQL。
- 部署 DB：Managed PostgreSQL。
- 圖片正式環境：S3 / R2 / MinIO 等 object storage。
- Ollama：本機或獨立 GPU / VPS，不建議免費雲端直接跑大型模型。

## Phase 14 Web Deployment 方向（規劃）

- 本輪 Web deployment baseline 先固定：
  - backend -> Render
  - frontend -> Vercel
- AI server / Ollama 暫不列入本輪免費雲端部署範圍。
- 金流 callback / notify 需要公開網址，因此先完成 Web deployment 再進入 NewebPay runtime 串接。

## Phase 14-2：Web Deployment Baseline（Render + Vercel）

### 部署拓樸

- backend：Render Web Service
- frontend：Vercel
- DB：Render PostgreSQL（或同級 managed PostgreSQL）
- AI server / Ollama：本輪不部署

### 建議部署順序

1. 建立 Render PostgreSQL，取得 `DATABASE_URL`
2. 建立 Render backend service 並配置 env
3. 先執行 `alembic upgrade head`
4. backend `/health` 驗證通過
5. 建立 Vercel frontend 並設定 `VITE_API_BASE_URL`
6. 完成 smoke test 後再對外開放

### Render backend 建議設定（手動 baseline）

- Build Command：`pip install -r backend/requirements.txt`
- Start Command：`python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Root Directory：repo root（避免 Alembic/migrations 路徑遺失）

### 環境變數切分

Render backend 至少需要：

- `APP_ENV`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`（填入 Vercel 網域）
- `EMAIL_PROVIDER`
- `EMAIL_FROM_NAME`
- `EMAIL_FROM_ADDRESS`
- `PRODUCTION_EMAIL_PROVIDER`
- `RESEND_API_KEY`（當 `EMAIL_PROVIDER=production` + `PRODUCTION_EMAIL_PROVIDER=resend`）

Vercel frontend 至少需要：

- `VITE_API_BASE_URL`（指向 Render backend 公網 URL）

本輪不需填寫（AI）：

- `OLLAMA_BASE_URL`
- `OLLAMA_TEXT_BASE_URL`
- `OLLAMA_VISION_BASE_URL`
- `LLM_TEXT_MODEL`
- `LLM_VISION_MODEL`
- `AI_WORKER_*`

### 最小 smoke test

1. backend `GET /health` 回 200
2. frontend 首頁可載入
3. login 可用
4. `/pantry`、`/shopping`、`/settings` 可進入
5. admin 帳號可進入 `/admin/members`
6. 前端 API 請求打到 Render backend domain
7. CORS 允許 Vercel domain，拒絕非 allowlist 網域
8. `alembic current` revision 到 head

## 使用者過多與服務穩定性

風險：backend CPU/RAM 不足、DB connection 過多、慢查詢、AI 推論阻塞、圖片佔用頻寬與儲存。

策略：managed PostgreSQL、水平擴充 API server、DB index、pagination、query limit、background job queue、object storage、rate limit、health check、logging、retry 上限。

## Background Job 規劃

Phase 08～12 採 job-based 流程，backend 不同步等待 AI 任務：

```text
POST 建立任務 → 回傳 job_id → worker 執行 → GET 查詢狀態 → 前端顯示結果
```

階段策略：

- Phase 08-0～08-2：PostgreSQL `ai_jobs` + DB polling worker，不新增 Redis/Celery/RQ/Dramatiq/RabbitMQ。
- Phase 09～12：Vision/Nutrition 共用 `ai_jobs`，一律使用 DB polling worker。
- Phase 13：再升級 queue（評估 RQ + Redis）。
- RabbitMQ 暫不採用，僅在未來需要複雜 message routing/事件流時評估。

## AI 服務與環境變數規劃（本次僅文件）

建議 `.env` 增補：

```env
AI_SERVER_HOST=0.0.0.0
AI_SERVER_PORT=8100
AI_WORKER_POLL_INTERVAL_SECONDS=5
AI_WORKER_BATCH_SIZE=1
AI_JOB_TIMEOUT_SECONDS=300
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEXT_BASE_URL=
OLLAMA_VISION_BASE_URL=
LLM_TEXT_MODEL=qwen2.5:7b
LLM_VISION_MODEL=qwen3-vl:8b
```

本地與雲端資源限制補充：

- `OLLAMA_TEXT_BASE_URL` / `OLLAMA_VISION_BASE_URL` 留空時，會 fallback 到 `OLLAMA_BASE_URL`，適合 MVP 快速啟動，但不代表效能隔離。
- worker process 分開（recipe/vision）只隔離 job process，不隔離模型推論硬體。
- 同一台機器即使用不同 port 跑兩個 Ollama instance，若共用同一張 GPU/CPU，仍可能互相搶資源。
- 雲端若同機同時跑 backend、recipe worker、vision worker、text Ollama、vision Ollama，會與本地同樣遇到資源競爭。
- 較佳部署：backend 與 AI worker 分離，recipe worker 指向 text runtime、vision worker 指向 vision runtime。
- 完整隔離：text/vision Ollama 分別部署到不同機器或不同 GPU，例如：
  - `OLLAMA_TEXT_BASE_URL=http://ollama-text.internal:11434`
  - `OLLAMA_VISION_BASE_URL=http://ollama-vision.internal:11434`
- 高負載階段再於 Phase 13 評估 RQ + Redis、worker replicas、不同 job queue、GPU worker pool。

docker-compose 後續規劃：

- 新增 `ai-server` 或 `ai-worker` service（共用同一個 PostgreSQL）。
- Phase 08～12 不新增 `redis` service。
- Phase 13 若採 RQ + Redis，再新增 `redis` service。

## Migration 與部署規範（Phase 12-3）

- deployment 前必須執行：`alembic upgrade head`
- production 不可使用 drop/recreate DB 作為升級方式。
- migration 失敗必須中止 deployment，不可忽略錯誤繼續上線。
- 需區分 development / staging / production migration 流程與驗收步驟。
- 需有 migration rollback 策略與 failure handling 文件。
- MVP 與目前 production deployment 的 AI 任務仍使用 PostgreSQL `ai_jobs` + DB polling worker。

### Deployment 前 Migration Checklist

1. 確認 migration 檔案已提交且 `alembic heads` 狀態正確。
2. 確認目標環境 `DATABASE_URL` 與 secret 設定正確（不可混用環境 DB）。
3. production 升級前先建立 DB backup/snapshot。
4. 執行 `alembic upgrade head`。
5. 執行 `alembic current` + `GET /health` 作最小驗收。

### Environment 差異

- development：開發者本機手動執行 migration 與基本 smoke test。
- staging：先執行 migration，再做部署前回歸驗收；失敗即停止 staging rollout。
- production：先 backup/snapshot，再 migration，成功後才能 rollout app。

### Failure Handling / Rollback

- `alembic upgrade head` 任一步驟失敗，部署流程必須立即停止。
- 可逆 schema 變更可評估 `alembic downgrade -1`。
- 若為不可逆或高風險變更，優先使用 DB backup/snapshot restore。
- 僅回滾 app 版本不足以處理 schema 問題時，不可單獨做 app rollback。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ


## Email Reminder 與成本注意事項（Phase 10/11）

到期 Email Reminder 會產生寄信成本與寄送限制風險。MVP 預設使用 `fake`（不寄真信）；開發/測試可用 `gmail_smtp`；正式環境建議 `production provider`（Resend / SendGrid / Amazon SES），並記錄發信量、失敗率、退信與 rate limit。

排程策略：

- 每天上午 8:00 與下午 5:00 執行 expiration reminder worker / scheduler。
- worker 檢查每位使用者 `expiration_email_reminder_days` 設定。
- 同一使用者同一天同一 send window 只能成功寄送一次。
- 使用 delivery log 避免重複寄送。
- 單元測試不可寄真信，需使用 fake email client。

Phase 11 子階段：

- `Phase 11-0`：Email Provider 策略與文件調整。
- `Phase 11-1`：Gmail SMTP 真實寄信（dev/test/少量）。
- `Phase 11-2`：Production Email Provider（Resend/SendGrid/SES）。
- `Phase 11-3`：正式 scheduler / cron / docker deployment。
- `Phase 11-4`：retry / failure handling / monitoring。

Secret 管理：

- Gmail app password、provider API key、AWS 憑證只可放 `.env` 或秘密管理服務。
- `.env.example` 不可放任何真實 secret。
- repository 不可提交實際 secret。
- production provider 三選一即可，不需同時申請 Resend/SendGrid/SES 三組帳號。
- Phase 11-2 目前僅支援 Resend；SendGrid/SES 仍為未實作預留。

Gmail SMTP 額外限制：

- Gmail SMTP 僅建議開發/測試/少量寄送。
- 正式大量寄送請改用 production provider（Phase 11-2）。

手機 App 未來通知策略：

- 提醒規則應保留在 server，讓 Web / iOS / Android 共用。
- 手機 App 未來可新增 push token，由 server 決定何時提醒，mobile 只負責顯示 push notification。

## Phase 11-3：Scheduler / Cron / Docker Deployment

到期提醒排程在 Phase 11-3 以簡單穩定方案部署，不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。

### Linux cron（建議）

- 設定 `CRON_TZ=Asia/Taipei`
- 每日 08:00 執行 morning_08
- 每日 17:00 執行 evening_17

### Docker Compose scheduler service

- backend API 與 scheduler 拆成不同 container
- scheduler 只執行 `python -m backend.app.jobs.expiration_email_runner`
- 可使用 `docker-compose.scheduler.prod.yml` 作為 production override

### 注意事項

- DB datetime 一律 UTC，排程觸發時區由部署環境（`SCHEDULER_TIMEZONE`）控制
- 重複寄送主要由 delivery log success 去重保護
- retry/monitoring 在 Phase 11-4 才實作
- production secrets（SMTP password/API key）不可提交 git

## Phase 11-4 部署注意事項

- `.env` 新增 `EMAIL_RETRY_MAX_ATTEMPTS=1`
- 允許 `0~3`，超過範圍設定應失敗
- 預設補發 1 次，避免對錯誤收件地址重複轟炸
- 監控以 structured logs 為主（本階段不導入 metrics/alert service）
- 不可在 log 中輸出 secret（API key / SMTP password / Authorization）
