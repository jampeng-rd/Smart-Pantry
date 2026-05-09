# 測試規範

## 後端測試

後端每個功能都必須有單元測試，放在 `backend/tests/`。

## 必測功能

- health API。
- auth service：註冊、登入、密碼錯誤。
- refresh token：refresh 成功、過期、revoke / logout、無效 token。
- pantry service：新增、編輯、刪除、查詢、pagination。
- expiration service：即將過期、已過期。
- shopping service：新增、標記已購買、刪除。
- recipe service：prompt 組裝與 LLM mock。
- ocr import service：OCR mock 與候選資料整理。
- nutrition service：粗估結果 parsing 與聲明。

## LLM / OCR 測試

不可在單元測試直接呼叫真實 Ollama 或外部 OCR。使用 fake client / stub client。

AI job 測試原則（Phase 08～11）：
- 不可在單元測試中呼叫真實 Ollama。
- 使用 fake AI client / fake worker。
- 測試 job 建立。
- 測試狀態轉換：`pending -> running -> success`。
- 測試 `failed` 狀態與 `error_message`。
- 測試跨使用者不可查詢 job。
- 測試 worker 不處理其他使用者不相干資料（僅處理被 claim 的 pending job）。
- recipe recommendation 需測兩種模式：
  - `selected_items`：建立成功、空陣列錯誤、跨使用者 pantry item 驗證失敗
  - `auto_from_pantry`：可建立 pending job，且 input snapshot 記錄 recommendation_mode

## API 測試

使用 FastAPI TestClient 或 httpx。測試成功與失敗案例，並確認 response 格式符合 `agent-docs/api.md`。

時間欄位需額外驗證：
- 新建立資料的 datetime 回傳需包含時區（`Z` 或 `+00:00`）。
- `purchased_at` 在 `is_purchased=true` 時需包含時區；`is_purchased=false` 時為 `null`。
- 後端與 DB 使用 UTC timezone-aware datetime，避免 naive datetime。

## Web 測試

v1 可先做 TypeScript 型別檢查、npm build、核心 utility function 測試、theme 切換 utility、tokenService refresh 行為測試。

```bash
cd frontend
npm run build
```

- Phase 06 MVP 需驗證使用瀏覽器 `Intl API` 將 UTC datetime 轉成本地時間顯示。
- 若後續加入 `user_preferences.timezone`，需驗證可覆蓋瀏覽器時區。


## Token 與儲存測試補充

- refresh token 必須測試 hash 儲存，不可儲存明文 token。
- 測試 access token 過期後可透過 refresh token 取得新 access token。
- 測試 logout / revoke 後 refresh token 不可再使用。
- 前端 tokenService 需測試 sessionStorage 儲存、快過期 refresh、401 後最多重試一次。

## 圖片與 Background Job 測試補充

- 圖片上傳需測試超過 5MB 時拒絕。
- 測試 DB 僅保存 image_path / image_url，不保存圖片 blob/base64。
- Phase 08～11 以 job-based 為主：需測 job 建立、狀態查詢、成功與失敗案例。
- Phase 12 若導入 RQ + Redis，需補測 enqueue、worker process、retry、失敗重試策略。

## Shopping 與 Pantry 關係測試補充

- 測試 `source_pantry_item_id` 僅做來源關聯，不會自動更新 pantry。
- 測試標記 `is_purchased=true` 只更新 shopping item 狀態與 `purchased_at`。
- 若未來新增 convert-to-pantry API，需測必填欄位確認流程（`name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note`）。
