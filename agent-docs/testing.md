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

## API 測試

使用 FastAPI TestClient 或 httpx。測試成功與失敗案例，並確認 response 格式符合 `agent-docs/api.md`。

## Web 測試

v1 可先做 TypeScript 型別檢查、npm build、核心 utility function 測試、theme 切換 utility、tokenService refresh 行為測試。

```bash
cd frontend
npm run build
```


## Token 與儲存測試補充

- refresh token 必須測試 hash 儲存，不可儲存明文 token。
- 測試 access token 過期後可透過 refresh token 取得新 access token。
- 測試 logout / revoke 後 refresh token 不可再使用。
- 前端 tokenService 需測試 sessionStorage 儲存、快過期 refresh、401 後最多重試一次。

## 圖片與 Background Job 測試補充

- 圖片上傳需測試超過 5MB 時拒絕。
- 測試 DB 僅保存 image_path / image_url，不保存圖片 blob/base64。
- AI / OCR MVP 可測同步流程；若加入 background job，需測 job 建立、狀態查詢、成功與失敗案例。
