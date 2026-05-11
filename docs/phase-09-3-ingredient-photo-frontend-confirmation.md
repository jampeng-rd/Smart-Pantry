# Phase 09-3：食材辨識前端 UI + 使用者確認寫入 Pantry

## 目標

完成食材辨識前端可操作流程：上傳圖片建立 job、輪詢狀態、顯示候選食材、由使用者確認後逐筆寫入 pantry。  
本階段不修改 Phase 09-1 upload API、不修改 Phase 09-2 Vision worker、不新增 bulk API。

## 本階段完成內容

1. 路由與頁面
- 使用 `/ingredients` route。
- Sidebar 文案調整為「食材辨識」。
- 使用既有 Dashboard layout / TopToolbar / theme variables。

2. 前端狀態管理
- 新增 `frontend/src/features/ingredients/ingredientTypes.ts`
- 新增 `frontend/src/features/ingredients/ingredientSlice.ts`
- Store 新增 `ingredients` reducer（不影響 recipes/pantry/shopping slice）

3. API client
- `frontend/src/services/apiClient.ts` 新增：
  - `ingredientsApi.createIngredientPhotoJob(file)`
  - `ingredientsApi.getIngredientPhotoJob(jobId)`
- 上傳使用 `multipart/form-data`，field name 固定為 `image`
- frontend 僅呼叫 backend，不直連 `ai_server`

4. 上傳與前置檢查
- 格式限制：`image/jpeg`、`image/png`、`image/webp`
- 大小限制：<= 5MB（前端先擋）
- 提供圖片預覽與拍攝建議提示文字

5. Job polling
- pending/running 顯示「AI 正在辨識食材」
- success/failed 停止 polling
- unmount 清除 interval，避免 memory leak
- 切頁回來若任務仍 pending/running，自動恢復 polling

6. 候選食材確認
- success 後顯示 candidate list
- 每筆可編輯欄位：
  - `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`
- 每筆可刪除
- 前端驗證：
  - `name/category/quantity/unit` 必填
  - `quantity > 0`

7. 寫入 pantry
- 按「確認加入庫存」後逐筆呼叫既有 `pantryApi.create`
- 不新增 bulk API
- 部分成功/部分失敗時顯示失敗項目與中文錯誤原因
- job success 不會自動寫入 pantry，必須使用者手動確認

8. 暫存上傳圖片清理（temporary upload cleanup）
- `uploads/ingredient_photos/` 僅作 Vision 辨識暫存，不作長期保存。
- worker 在 `ingredient_photo` job 進入終態後會嘗試刪除 `input_snapshot.image_path`：
  - success
  - failed
  - timeout
  - stale running -> failed
- 僅刪除 `uploads/` 目錄內檔案（防止 path traversal）。
- 若檔案不存在或刪除失敗，worker 只記錄 warning，不會覆蓋既有 job success/failed 結果。
- `ai_jobs` 與 `result.candidate_items` 仍保留；前端候選顯示與使用者確認寫入 pantry 不受影響。

9. worker isolation 使用提醒（Phase 09 收尾補充）
- `job_type isolation` 是 worker process 層級隔離。
- 若單一 worker process 啟用 `recipe_recommendation,ingredient_photo`，任務仍在同一 process 逐筆處理，可能互相等待。
- 若要降低 recipe 被 Vision 任務拖慢，建議分開啟動兩個 process：
  - `python -m ai_server.workers.job_worker --job-types recipe_recommendation`
  - `python -m ai_server.workers.job_worker --job-types ingredient_photo`
- 即使分開 process，若共用同一個 Ollama runtime/GPU/CPU，仍可能互相影響推論效能。

## 錯誤處理

- 前端不顯示 traceback / Pydantic 原始錯誤 / `NetworkError` 原文
- 轉換為中文友善訊息
- timeout 訊息沿用 backend 回傳：
  `食材照片辨識逾時，請改用較清楚、單一或少量食材的照片後再試。`

## MVP 使用範圍與限制

- 主要支援單一或少量未加工食材辨識
- 複雜場景（整桌料理、冰箱全景、多人餐點、過多品項）可能造成 timeout
- `candidate_items` 為 AI 候選，仍需使用者確認後才可寫入 pantry
- 整桌料理/餐點照片較適合後續 Nutrition 階段，非本階段庫存匯入主要目標
- `input_snapshot.image_path` 為歷史上傳路徑紀錄，不保證檔案仍存在（可能已被 worker cleanup）。
