# Phase 09-2：Vision Model 食材候選辨識

## 目標

在既有 Phase 09-1 的 ingredient photo job-based 架構上，將 worker 從固定 mock 候選改為透過 Vision model 產生 `candidate_items`，並維持 backend 非同步、frontend 不直連 ai_server。

## 本階段完成內容

1. 新增 Vision client：
- `ai_server/app/clients/ingredient_vision_client.py`
- 封裝 LangChain + Ollama Vision（`llm_vision_model`）
- 讀取圖片、轉 base64、呼叫模型、回傳文字輸出

2. 新增 ingredient photo recognition service：
- `ai_server/app/services/ingredient_photo_recognition_service.py`
- 負責 prompt、JSON parsing、schema 驗證、中文錯誤轉換

3. worker ingredient_photo handler 升級：
- `ai_server/workers/job_worker.py`
- `ingredient_photo` job 改呼叫 `IngredientPhotoRecognitionService`
- 保持 `job_type` isolation，不影響 `recipe_recommendation` 流程

4. result 格式維持 Phase 09-1 相容：

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
      "note": "AI 辨識候選，請確認"
    }
  ],
  "note": "AI 食材照片辨識結果，請使用者確認後再加入庫存。"
}
```

## 錯誤處理

- Vision 回傳非 JSON：job `failed`，中文錯誤訊息。
- 缺欄位或欄位格式錯誤：job `failed`，中文錯誤訊息。
- 圖片不存在：job `failed`，中文錯誤訊息。
- 模型呼叫異常：job `failed`，中文錯誤訊息。
- 不回傳 traceback 給使用者。

## 測試策略

- 單元測試全部使用 fake vision client，不呼叫真實 Ollama。
- 驗證成功解析、非 JSON、缺欄位、圖片不存在、worker 不寫入 pantry_items。
- 既有 recipe worker 測試需維持通過。

## 階段結論

Phase 09-2 已接入 Vision model 的 worker-side 推論路徑，仍維持 job-based 非同步流程與資料安全邊界（不直接寫入 pantry）。Phase 09-3 再完成前端候選確認與寫入流程。
