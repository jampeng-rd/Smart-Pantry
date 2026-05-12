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
feature/phase-11-ai-queue-worker-scaling
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

## 使用者過多與服務穩定性

風險：backend CPU/RAM 不足、DB connection 過多、慢查詢、AI 推論阻塞、圖片佔用頻寬與儲存。

策略：managed PostgreSQL、水平擴充 API server、DB index、pagination、query limit、background job queue、object storage、rate limit、health check、logging、retry 上限。

## Background Job 規劃

Phase 08～11 採 job-based 流程，backend 不同步等待 AI 任務：

```text
POST 建立任務 → 回傳 job_id → worker 執行 → GET 查詢狀態 → 前端顯示結果
```

階段策略：

- Phase 08-0～08-2：PostgreSQL `ai_jobs` + DB polling worker，不新增 Redis/Celery/RQ/Dramatiq/RabbitMQ。
- Phase 09～11：Vision/Nutrition 共用 `ai_jobs`；若延遲可接受，持續 DB polling。
- Phase 12：再升級 queue（首選 RQ + Redis，備選 Dramatiq + Redis）。
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
- 高負載階段再於 Phase 11 評估 RQ + Redis、worker replicas、不同 job queue、GPU worker pool。

docker-compose 後續規劃：

- 新增 `ai-server` 或 `ai-worker` service（共用同一個 PostgreSQL）。
- Phase 08～11 不新增 `redis` service。
- Phase 12 若採 RQ + Redis，再新增 `redis` service。

## Phase 09-0：AI Worker 架構調整 / job_type 隔離

- worker 可依 job_type 過濾任務
- 避免 Vision 任務拖慢 recipe_recommendation
- 可用 env 或 CLI 指定 worker 處理的 job types
- 暫不導入 Redis / Celery / RQ / Dramatiq / RabbitMQ


## Email Reminder 與成本注意事項（Phase 10）

到期 Email Reminder 會產生寄信成本與寄送限制風險。MVP 可先使用具免費額度的 Email provider 或 fake/log email client；正式環境需選擇 Resend、SendGrid、Amazon SES、Mailgun 等服務之一，並記錄發信量、失敗率、退信與 rate limit。

排程策略：

- 每天上午 8:00 與下午 5:00 執行 expiration reminder worker / scheduler。
- worker 檢查每位使用者 `expiration_email_reminder_days` 設定。
- 同一使用者同一天同一 send window 只能成功寄送一次。
- 使用 delivery log 避免重複寄送。
- 單元測試不可寄真信，需使用 fake email client。

手機 App 未來通知策略：

- 提醒規則應保留在 server，讓 Web / iOS / Android 共用。
- 手機 App 未來可新增 push token，由 server 決定何時提醒，mobile 只負責顯示 push notification。
