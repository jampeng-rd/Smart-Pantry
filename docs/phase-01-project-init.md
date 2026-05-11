# Phase 01：專案初始化

## 1. 階段目標

建立最小可運作且可擴充的全端基礎架構，包含 FastAPI、React + Vite + TypeScript + Redux Toolkit、PostgreSQL Docker Compose、CI 與基本測試。

## 2. 完成內容

- 建立 `backend/`、`frontend/`、`docs/` 基礎目錄與模組。
- 建立 FastAPI 最小後端應用與 `/health` API。
- 建立 API Layer、Service Layer、Domain Layer、Infra Layer 分層。
- 建立資料庫設定與 DB engine / session factory 集中管理。
- 建立 `backend/tests/test_health_api.py`。
- 建立 React + Vite + TypeScript 前端專案骨架。
- 建立 Redux Toolkit store 與 `auth/pantry/expiration/shopping/recipes/ingredients/nutrition/theme` feature 骨架。
- 建立主題架構 `light-soft` 與 `dark-soft`（基礎版本）。
- 建立 `docker-compose.yml`（`backend` + `smartpantry-db`）。
- 建立 GitHub Actions CI（backend pytest + frontend build）。
- 更新 `README.md` 為 Phase 01 狀態。

## 3. 涉及檔案

- `backend/requirements.txt`
- `backend/Dockerfile`
- `backend/app/main.py`
- `backend/app/api/health.py`
- `backend/app/services/health_service.py`
- `backend/app/domain/schemas/health_schema.py`
- `backend/app/infra/settings.py`
- `backend/app/infra/database.py`
- `backend/tests/test_health_api.py`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/app/store.ts`
- `frontend/src/app/hooks.ts`
- `frontend/src/features/*`
- `frontend/src/services/apiClient.ts`
- `frontend/src/services/tokenService.ts`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/globals.css`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `README.md`

## 4. 如何啟動

後端：`python -m uvicorn backend.app.main:app --reload`

前端：`cd frontend && npm run dev`

Docker：`docker compose up --build`

## 5. 單元測試

全部測試：`pytest backend/tests -q`

## 6. Web UI 測試方式

1. `cd frontend && npm install && npm run dev`
2. 開啟瀏覽器進入 Vite 顯示網址。
3. 確認首頁顯示繁體中文標題與 Phase 01 訊息。
4. 點擊「切換主題」按鈕，確認 `light-soft` / `dark-soft` 主題切換。

## 7. API 串接說明

- 目前僅開放 `GET /health`。
- Route 僅做依賴注入與回傳，狀態組裝放在 `HealthService`。
- 後續業務 API 需依功能分檔，避免集中在單一 route 或 service。

## 8. PostgreSQL 測試方式

1. `docker compose up -d smartpantry-db`
2. 使用 `SMARTPANTRY_DATABASE_URL` 指向 `smartpantry-db` 或本機 `localhost:5432`。
3. 後端目前已具備連線工廠（engine + session factory）架構，後續 phase 可直接接入 repository 與 migration。

## 9. 效能與擴充性注意事項

- DB 連線：已集中於 `infra/database.py`，避免每請求重建 engine。
- Pagination：本 phase 尚無列表 API；Phase 03 起所有列表 API 必須支援 `page/page_size`。
- Index：本 phase 尚未建立資料表；Phase 02/03 起需針對 `user_id`、時間與查詢欄位建立索引。
- AI 任務延遲：本 phase 未實作 AI/Ingredient Recognition；後續可能因推論時間阻塞 API，需保留 background job 化能力。
- 背景任務：尚未導入 Celery/RQ/Dramatiq；先保持 service 與 infra 解耦，利於後續拆分 worker。
- 水平擴充：目前為單 backend instance；建議後續加入 stateless session、rate limit 與觀測性指標。
- CI 風險：目前 CI 僅跑 pytest 與 frontend build，後續需補 lint、型別檢查與安全掃描。

## 10. 已知限制

- 尚未實作 auth、refresh token、pantry CRUD、AI、食材辨識、nutrition、background job。
- 尚未加入 DB migration 工具（例如 Alembic）。
- 前端 theme 狀態目前未持久化，僅提供架構。

## 11. 下一階段建議

- 進入 Phase 02，實作 auth 註冊/登入與 refresh token 全流程。
- 建立 `users` 與 `refresh_tokens` model/repository/service/API 與對應測試。
- 增加 token 安全策略與 401 重試機制測試。
