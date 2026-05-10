# Phase 09-1：食材照片辨識 Job API + Storage + Mock Worker

## 目標

本階段建立 ingredient photo 的 job-based 流程與圖片儲存能力，不接真實 Vision model，不改 frontend 直連策略。

## 本階段完成內容

1. backend 新增 ingredient photo job API：
- `POST /ingredients/photo/jobs`（multipart/form-data）
- `GET /ingredients/photo/jobs/{job_id}`

2. 上傳驗證規則：
- 限制圖片大小 `<= 5MB`
- 僅允許 `image/jpeg`、`image/png`、`image/webp`

3. 本機儲存封裝：
- `backend/app/infra/storage.py`
- 圖片寫入 `uploads/ingredient_photos/`
- 檔名採 UUID，不直接使用原始檔名
- DB / `ai_jobs.input_snapshot` 僅存 `image_path`、`original_filename`、`mime_type`、`size_bytes`
- 不存 blob/base64

4. worker mock handler：
- `job_type=ingredient_photo` 可由 worker claim 並處理
- mock result 產生 `candidate_items`
- 不直接寫入 `pantry_items`
- `failed` 使用中文友善錯誤訊息

5. Job 隔離：
- worker 可用 `--job-types ingredient_photo` 專門處理照片辨識任務
- `recipe_recommendation` 與 `ingredient_photo` 可分開啟動，避免互相影響

## Mock 輸出格式

```json
{
  "candidate_items": [
    {
      "name": "番茄",
      "category": "蔬菜",
      "quantity": 1,
      "unit": "顆",
      "expiration_date": null,
      "storage_location": "fridge",
      "note": "AI mock 辨識候選，請確認"
    }
  ],
  "note": "這是 mock 食材辨識結果，請使用者確認後再加入庫存。"
}
```

## 限制與下一步

- 本階段不接真實 Vision model（Phase 09-2 再導入）。
- 本階段不做使用者確認後寫入 pantry 的完整前端流程（Phase 09-3 實作）。
- Phase 09～10 仍沿用 PostgreSQL `ai_jobs` + DB polling worker，不導入 Redis/Celery/RQ/Dramatiq/RabbitMQ。
