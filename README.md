# 智慧食材保存與膳食管理系統（Smart Pantry & Nutritionist）

## 專案狀態

```text
Phase 01：專案初始化 ✅
Phase 02：使用者註冊 / 登入 + Refresh Token ✅
Phase 03：手動食材庫存管理 ✅
Phase 04：食材分類、過期提醒與狀態篩選 ✅
Phase 05：購物清單 ⏳
Phase 06：前端完整 UI + 主題切換 ⏳
Phase 07：CI/CD 與部署 ⏳
Phase 08：AI 食譜推薦 ⏳
Phase 09：發票 / 收據 OCR 匯入 ⏳
Phase 10：食材照片辨識 ⏳
Phase 11：餐點營養粗估 ⏳
```

## 環境需求

Python 3.10+、Node.js 20+、Docker、PostgreSQL、Ollama（AI 階段）。

## 環境變數

請先複製 `.env.example` 為 `.env`，並填入本機設定。`.env` 不可提交到版本控制，`.env.example` 僅放範例值，不可放真實 secret。

## 後端啟動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

## 前端啟動

```bash
cd frontend
npm install
npm run dev
```

## Docker Compose 啟動

```bash
docker compose up --build
```

## Auth 與 Token

已完成 `register/login/refresh/logout/me`：
- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- Refresh token 僅存 DB hash，不存明文。
- `logout` 會撤銷 refresh token，撤銷後 refresh 會失敗。

MVP 前端可使用 sessionStorage 儲存 token（有 XSS 風險）；正式環境建議 refresh token 改為 httpOnly secure cookie。

## Pantry 與 Expiration

已完成：
- `POST /pantry/items`
- `GET /pantry/items`（支援 `page/page_size/category/q/sort=expiration_date/status`）
- `PATCH /pantry/items/{item_id}`
- `DELETE /pantry/items/{item_id}`
- `GET /expiration/summary`

狀態規則：
- `expired`：`expiration_date < 今天`
- `expiring_soon`：`今天 <= expiration_date <= 今天 + 7 天`
- `normal`：其他情況，`expiration_date=null` 視為 `normal`

所有 pantry/expiration 查詢都強制綁定目前登入 `user_id`，不可跨使用者讀寫。

## 前端 UI

主要介面使用繁體中文，按鈕與導覽使用 react-icons，支援柔和亮色與柔和暗色主題。

## AI 功能限制

AI 食譜為生活建議；OCR / 食材照片辨識結果需由使用者確認；餐點營養估算僅供生活參考。

## 效能與擴充性

開發階段以本地 Docker PostgreSQL 為主，部署階段使用 managed PostgreSQL。列表 API 使用 pagination，常用查詢需 DB index，AI / OCR / 圖片處理 MVP 可同步呼叫，後續可改 Celery / RQ / Dramatiq background job。圖片不存 DB blob/base64；DB 只存 image_path / image_url。
