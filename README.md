# 智慧食材保存與膳食管理系統（Smart Pantry & Nutritionist）

## 專案狀態

```text
Phase 01：專案初始化 ✅
Phase 02：使用者註冊 / 登入 + Refresh Token ⏳
Phase 03：手動食材庫存管理 ⏳
Phase 04：食材分類、過期提醒與狀態篩選 ⏳
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

使用 access token + refresh token。Access token 預設 15 分鐘，refresh token 預設 7 天。MVP 前端可使用 sessionStorage 儲存 token，但需標示 XSS 風險；正式環境建議 refresh token 改用 httpOnly secure cookie。

> Phase 01 尚未實作登入、refresh token 與 token 流程，本段為後續階段規劃。

## 前端 UI

主要介面使用繁體中文，按鈕與導覽使用 react-icons，支援柔和亮色與柔和暗色主題。

## AI 功能限制

AI 食譜為生活建議；OCR / 食材照片辨識結果需由使用者確認；餐點營養估算僅供生活參考。

## 效能與擴充性

開發階段以本地 Docker PostgreSQL 為主，部署階段使用 managed PostgreSQL。列表 API 使用 pagination，常用查詢需 DB index，AI / OCR / 圖片處理 MVP 可同步呼叫，後續可改 Celery / RQ / Dramatiq background job。圖片不存 DB blob/base64；DB 只存 image_path / image_url，圖片正式環境使用 S3 / R2 / MinIO。
