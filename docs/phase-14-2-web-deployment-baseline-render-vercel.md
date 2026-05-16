# Phase 14-2：Web Deployment Baseline（Render + Vercel）

## 目標

將目前專案整理成可由維運者手動部署的 baseline，完成 backend(Render) + frontend(Vercel) + managed PostgreSQL 的最小可上線流程與驗收規範。

## 本階段範圍

- 明確定義 Render backend 部署步驟。
- 明確定義 Vercel frontend 部署步驟。
- 明確定義雲端 migration（`alembic upgrade head`）的執行時機與失敗處理。
- 切分 Render / Vercel / 本輪不需填寫的環境變數。
- 建立 deployment 後最小 smoke test checklist。

## 非本階段範圍

- 不進入 Phase 14-3 Billing runtime。
- 不部署 AI server / Ollama。
- 不調整與部署文件無關的 runtime 功能。

## Repo 盤點結果（部署基礎）

目前已具備：

1. Backend 可用 `uvicorn` 啟動（`backend.app.main:app`），且有 `GET /health`。
2. Frontend 已支援 `VITE_API_BASE_URL`（`frontend/src/services/apiClient.ts`）。
3. Backend 已支援 CORS allowlist（`CORS_ORIGINS`，逗號分隔）。
4. Alembic migration 已建立（`alembic.ini` + `migrations/`），且 `migrations/env.py` 會使用 `DATABASE_URL`。
5. CI 已有 backend tests + frontend build（`.github/workflows/ci.yml`）。
6. PostgreSQL schema 由 migration 管理（Phase 12-1 / 12-3 已建立規範）。

仍需補齊（本階段完成）：

1. Render 與 Vercel 分平台部署步驟文件。
2. Render 與 Vercel 環境變數切分清單。
3. 雲端 migration 與 deployment 順序、失敗中止規範。
4. deployment baseline 驗收與 smoke test checklist。

## 部署拓樸（本輪）

- Render Web Service：部署 `backend/` FastAPI。
- Render PostgreSQL：提供 production `DATABASE_URL`。
- Vercel Project：部署 `frontend/` React + Vite 靜態站。
- browser 僅呼叫 backend API，不直連 `ai_server`。

## 部署順序建議

1. 建立 Render PostgreSQL，取得 production `DATABASE_URL`。
2. 建立 Render backend service，先完成必要 env 設定。
3. 於 Render 對 production DB 執行 `alembic upgrade head`。
4. backend 啟動成功並通過 `/health`。
5. 建立 Vercel frontend，設定 `VITE_API_BASE_URL` 指向 Render backend 公網 URL。
6. 執行 deployment smoke test。

## Render Backend 部署步驟

以下流程為手動部署 baseline（不要求自動化 pipeline）：

1. Render 建立 `Web Service` 並連接本 repo。
2. Root Directory：repo 根目錄（不要切到 `backend/` 子資料夾，避免 Alembic 找不到 `migrations/`）。
3. Build Command：
   - `pip install -r backend/requirements.txt`
4. Start Command：
   - `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. 設定 Render backend env（見下方「環境變數切分」）。
6. 確認 service 可啟動，並用 `GET /health` 驗證。

## Render PostgreSQL / DATABASE_URL 使用方式

1. 在 Render 建立 PostgreSQL instance。
2. 取得 Internal/External `DATABASE_URL`（依 Render 文件與網路拓樸選擇）。
3. 將 `DATABASE_URL` 設為 backend service env。
4. Render 上執行 migration：
   - `alembic upgrade head`
5. migration 成功後，以 `alembic current` 驗證 revision 已到 head。

注意：

- migration 失敗必須中止 deployment，不可繼續 rollout。
- production 不可使用 drop/recreate DB 當升級方式。

## Vercel Frontend 部署步驟

1. Vercel 匯入本 repo。
2. Project Root 設定為 `frontend/`。
3. Build command：`npm run build`
4. Output directory：`dist`
5. 設定 env：
   - `VITE_API_BASE_URL=https://<your-render-backend-domain>`
6. 重新部署 frontend，確認 API 請求導向正確 backend。

## 環境變數切分（Phase 14-2 Baseline）

### Render Backend 必要 env

最小必要：

- `APP_ENV=production`
- `DATABASE_URL=<render-postgresql-url>`
- `JWT_SECRET_KEY=<strong-random-secret>`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=15`
- `REFRESH_TOKEN_EXPIRE_DAYS=7`
- `CORS_ORIGINS=https://<your-vercel-domain>`

建議補齊：

- `APP_NAME=Smart Pantry API`
- `SCHEDULER_TIMEZONE=Asia/Taipei`
- `EMAIL_PROVIDER=fake|gmail_smtp|production`
- `EMAIL_RETRY_MAX_ATTEMPTS=1`
- `EMAIL_FROM_NAME=Smart Pantry`
- `EMAIL_FROM_ADDRESS=<verified-sender>`
- `PRODUCTION_EMAIL_PROVIDER=resend|sendgrid|ses`
- `RESEND_API_KEY=<required when production+resend>`

依 provider 條件填寫：

- `GMAIL_SMTP_HOST`
- `GMAIL_SMTP_PORT`
- `GMAIL_SMTP_USERNAME`
- `GMAIL_SMTP_APP_PASSWORD`
- `SENDGRID_API_KEY`（future）
- `AWS_SES_REGION`（future）
- `AWS_SES_ACCESS_KEY_ID`（future）
- `AWS_SES_SECRET_ACCESS_KEY`（future）

### Vercel Frontend 必要 env

- `VITE_API_BASE_URL=https://<your-render-backend-domain>`

### 本輪暫不部署，可不填（AI server / Ollama）

- `AI_SERVER_HOST`
- `AI_SERVER_PORT`
- `AI_WORKER_POLL_INTERVAL_SECONDS`
- `AI_WORKER_BATCH_SIZE`
- `AI_WORKER_JOB_TYPES`
- `AI_JOB_TIMEOUT_SECONDS`
- `AI_VISION_TIMEOUT_SECONDS`
- `OLLAMA_BASE_URL`
- `OLLAMA_TEXT_BASE_URL`
- `OLLAMA_VISION_BASE_URL`
- `LLM_TEXT_MODEL`
- `LLM_VISION_MODEL`

## Migration 與部署流程（雲端）

強制規範：

1. Render 雲端部署也必須執行 Alembic migration。
2. `alembic upgrade head` 不是只給本地開發用。
3. migration 執行位置在「backend rollout 前」。
4. migration failure 必須中止 deployment。
5. production 不可用 drop/recreate DB。

建議順序：

1. 設定 `DATABASE_URL` 到 production DB。
2. 執行 `alembic upgrade head`。
3. 驗證 `alembic current`。
4. 啟動/部署 backend service。
5. 驗證 `/health` 與基本 API。
6. 再部署 frontend。

## Deployment 後最小 Smoke Test

1. Backend 健康檢查：
   - `GET https://<render-backend>/health` 回 200。
2. Frontend 可載入：
   - `https://<vercel-frontend>` 可正常打開。
3. Login 可用：
   - 可登入既有帳號（或測試帳號）。
4. 基本路由可進入（已登入）：
   - `/pantry`
   - `/shopping`
   - `/settings`
   - `/admin/members`（admin 帳號）
5. Frontend API 導向：
   - 瀏覽器 network 顯示請求打到 Render backend domain。
6. CORS 正常：
   - 非預期網域不應通過；Vercel 網域可通過。
7. Migration revision 正常：
   - `alembic current` 等於預期 head。

## 為何 AI server / Ollama 不在本輪部署

1. Phase 14-2 目標是建立 Web deployment baseline，先滿足公開 Web URL 與核心 CRUD/Auth 可用。
2. Billing callback/notify 需要先有穩定公開 Web 入口，優先順序高於 AI runtime。
3. AI runtime 牽涉 GPU/成本/worker 資源隔離，屬後續容量規劃，不是本階段 blocking item。
4. 目前產品路線允許 AI server 暫不部署，frontend 仍可透過既有核心功能完成主要流程。

## 驗收結論

- 本階段完成 Render + Vercel 的手動部署 baseline 文件。
- 完成環境變數切分、migration 先後順序與 failure handling 規範。
- 完成 deployment 最小 smoke test checklist。
- 未進入 Phase 14-3，未部署 AI server / Ollama。
