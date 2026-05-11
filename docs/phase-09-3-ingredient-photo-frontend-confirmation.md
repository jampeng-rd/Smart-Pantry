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
