# Phase 08-3：Recipes 前端 UI 串接

## 1. 階段目標

將 `/recipes` 從 placeholder 改為可操作的 AI 食譜推薦頁，且維持既有 job-based 後端行為：
- frontend 只呼叫 backend
- 建立 job 後立即回 `job_id`
- 前端輪詢 `GET /recipes/recommendation-jobs/{job_id}` 顯示狀態與結果

## 2. 本階段完成項目

- 新增 `recipesApi`：
  - `POST /recipes/recommendation-jobs`
  - `GET /recipes/recommendation-jobs/{job_id}`
- 重整 `features/recipes/recipeTypes.ts`：
  - job request/response 型別
  - result 型別
  - recipe state 型別
- 重整 `features/recipes/recipeSlice.ts`：
  - 載入 pantry（供 `selected_items` 多選）
  - 建立 job
  - 查詢 job status
  - 狀態管理（pending/running/success/failed/cancelled）
- `/recipes` UI 實作：
  - `selected_items` / `auto_from_pantry` 模式切換
  - 料理時間、工具、飲食偏好、過敏原、優先即將過期選項
  - selected mode 食材多選
  - pending/running/success/failed 中文狀態
  - success result 顯示（recipe_name / ingredients_used / missing_ingredients / steps / cooking_time_minutes / note）
  - failed 中文友善錯誤
- polling 清理：
  - job 完成（success/failed/cancelled）停止 polling
  - component unmount 清除 interval，避免 memory leak

## 3. 啟動方式

1. 啟動 backend（FastAPI）
2. 啟動 ai_worker（DB polling）
3. 啟動 frontend（Vite）

```bash
cd frontend
npm run dev
```

## 4. 手動測試步驟

1. `selected_items` 成功
- 進入 `/recipes`
- 選擇「自選食材」
- 勾選至少一筆 pantry 食材
- 輸入合法料理時間（正整數）
- 送出後觀察 `pending/running`，最後顯示成功結果

2. `auto_from_pantry` 成功
- 切換「自動從庫存挑選」
- 輸入合法料理時間
- 送出後觀察 `pending/running`，最後顯示成功結果

3. `failed` 顯示中文錯誤
- 在 worker 無可用食材、模型異常、或後端回 failed 的情境下送出任務
- 驗證前端顯示中文錯誤，不顯示 traceback 或原始技術錯誤

## 5. 驗證與錯誤處理

- `selected_items` 未選任何食材時，前端直接阻擋送出。
- `cooking_time_minutes` 非正整數時，前端直接阻擋送出。
- 網路與 API 失敗訊息轉成中文友善錯誤，不直接顯示 `NetworkError`、traceback 或 Pydantic 原始細節。

## 6. 已知限制

- MVP 的 pantry 選擇清單目前一次抓取前 200 筆，若資料量更大需導入搜尋/分頁選擇器。
- `cooking_tools`、`allergies` 目前使用逗號分隔文字輸入，未提供進階 tag 編輯器。
- 輪詢採固定間隔，尚未做指數退避（backoff）。

## 7. 效能與 Polling 注意事項

- 輪詢間隔為 2.5 秒，避免過度頻繁查詢。
- 任務進入 `success/failed/cancelled` 即停止 polling。
- 元件 unmount 時一定清除 interval，降低記憶體與多餘請求風險。
- 若 AI 任務量持續增加，Phase 12 再評估 queue 升級（RQ + Redis）。
