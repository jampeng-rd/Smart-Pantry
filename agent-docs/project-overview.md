# 專案總覽

## 專案名稱

中文名稱：智慧食材保存與膳食管理系統

英文名稱：Smart Pantry & Nutritionist

## 專案目標

建立一個可練習完整工程流程的智慧食材庫存與膳食管理系統，包含 FastAPI、React + Vite + TypeScript + Redux Toolkit、PostgreSQL、Docker Compose、單元測試、CI/CD、部署與 AI workflow。

## 核心產品概念

使用者手動管理家中食材，記錄數量、單位、分類與過期日。系統提醒即將過期與已過期食材，協助建立購物清單。後續 AI 根據庫存與偏好推薦料理，並透過 圖片辨識減少手動輸入成本。

## 主要使用流程

```text
註冊 / 登入
→ access token 快過期時自動 refresh
→ 手動新增食材
→ 查看即將過期食材
→ 加入購物清單
→ 採買後先標記已購買（僅記錄 purchased_at）
→ 使用者確認欄位後再更新庫存
→ AI 根據庫存推薦料理
→ 後續用食材照片輔助匯入
```

## 重要限制

- 不做醫療或專業營養診斷。
- AI 營養估算僅供生活參考。
- AI 辨識結果需使用者確認後才可寫入庫存。
- 不做整個冰箱照片辨識，只做單一或少量食材照片辨識。

## 效能與擴充性

MVP 可先使用單一 API server + PostgreSQL，但設計時需保留 pagination、DB index、背景任務、cache、水平擴充與 AI 任務分離的可能性。

## 補充架構決策

- 開發階段以本地 Docker PostgreSQL 為主，部署階段再使用 managed PostgreSQL。
- Access token 預設 15 分鐘，refresh token 預設 7 天，refresh token 只以 hash 形式存入 DB。
- MVP 前端可使用 sessionStorage 儲存 token，但需標示 XSS 風險；正式環境建議 refresh token 使用 httpOnly secure cookie。
- 後端與 DB 的 datetime 一律使用 UTC timezone-aware；API datetime 一律回傳含時區（`Z` 或 `+00:00`）。
- 前端顯示時間時再依瀏覽器 timezone 或 `user_preferences.timezone` 轉換本地時間；Phase 06 MVP 先用瀏覽器 `Intl API`。
- 圖片不可用 blob/base64 存入 PostgreSQL；開發階段可存本機 uploads/，正式環境使用 S3 / R2 / MinIO，DB 只存 image_path / image_url。
- AI / Vision MVP 可同步呼叫，任務變慢後改成 Celery / RQ / Dramatiq background job。
- AI 階段使用 LangChain 1.x 系列，LLM client 仍封裝在 infra 層。

## Shopping 與 Pantry 關係

- `pantry_items` 代表目前庫存，`shopping_list_items` 代表購物清單。
- `source_pantry_item_id` 表示來源關聯，不表示自動更新庫存。
- `is_purchased=true` 只代表已購買並記錄 `purchased_at`，不可自動寫入 pantry。
- 若需轉入庫存，必須由使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`。

## Web 系統 UI 架構

本專案 Web UI 為完整系統型 Dashboard，而非單頁工具。

主要流程：

```text
開啟網站
→ Login / Register Page
→ 登入/註冊成功
→ Pantry（/pantry）
→ Sidebar 導覽不同功能
→ Workspace 顯示功能頁
```

Dashboard 採：

- 左側 Sidebar
- 右側 Workspace
- 上方 Toolbar

Sidebar 底部固定顯示目前登入使用者。
點擊後向上展開使用者選單。

補充：

- `/dashboard` route 目前保留為未來總覽頁（placeholder）。
- MVP 側邊欄暫時隱藏「儀表板」導航項目。
