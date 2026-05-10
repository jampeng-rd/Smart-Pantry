# README 更新模板

## 專案名稱

智慧食材保存與膳食管理系統（Smart Pantry & Nutritionist）

## 專案狀態

```text
Phase 01：專案初始化 ✅
Phase 02：使用者註冊 / 登入 + Refresh Token ✅
Phase 03：手動食材庫存管理 ✅
Phase 04：食材分類、過期提醒與狀態篩選 ✅
Phase 05：購物清單 ✅
Phase 06-1：Auth UI + Protected Layout ✅
Phase 06-2：Dashboard + Sidebar + Theme ✅
Phase 06-3：Pantry UI ✅
Phase 06-4：Expiration UI ✅
Phase 06-5：Shopping UI ✅
Phase 06-6A：Pantry / Shopping 前端整合 UX 修正 ✅
Phase 06-6B：前端路由與登入導向整理 ✅
Phase 06-6C：前端共用元件盤點與小幅整理 ✅
Phase 07：CI/CD 與部署 ⏳
Phase 08-0：AI Server / AI Job 架構初始化 ✅
Phase 08-1：AI 食譜推薦 Mock（ai_jobs + fake worker）✅
Phase 08-2：AI 食譜推薦 LangChain + Ollama ✅
Phase 08-3：Recipes 前端 UI 串接 ✅
Phase 09-0：AI Worker 架構調整 / job_type 隔離 ⏳
Phase 09-1：食材照片辨識 Job API + Storage + Mock Worker ⏳
Phase 09-2：Vision Model 食材候選辨識 ⏳
Phase 09-3：食材辨識前端 UI + 使用者確認寫入 Pantry ⏳
Phase 10-1：營養粗估 Job API + Mock Worker ⏳
Phase 10-2：Vision/Text Model 營養粗估 ⏳
Phase 10-3：Nutrition 前端 UI + 生活參考聲明 ⏳
Phase 11：AI Queue / Worker Scaling（RQ + Redis，視需要）⏳
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

## Auth 與 Token

使用 access token + refresh token。Access token 預設 15 分鐘，refresh token 預設 7 天。MVP 前端可使用 sessionStorage 儲存 token，但需標示 XSS 風險；正式環境建議 refresh token 改用 httpOnly secure cookie。

## 前端 UI

主要介面使用繁體中文，按鈕與導覽使用 react-icons，支援柔和亮色與柔和暗色主題。

## AI 功能限制

AI 食譜為生活建議；食材照片辨識結果需由使用者確認；餐點營養估算僅供生活參考。

## 效能與擴充性

開發階段以本地 Docker PostgreSQL 為主，部署階段使用 managed PostgreSQL。列表 API 使用 pagination，常用查詢需 DB index，AI / 圖片處理 MVP 可同步呼叫，後續可改 Celery / RQ / Dramatiq background job。圖片不存 DB blob/base64；DB 只存 image_path / image_url，圖片正式環境使用 S3 / R2 / MinIO。

收據 OCR 暫不列入 MVP，未來若能取得商品明細再評估。
