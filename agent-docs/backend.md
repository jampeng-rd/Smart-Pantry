# 後端架構規範

## 技術棧

Python 3.10+、FastAPI、Pydantic v2、pydantic-settings、pytest、httpx、PostgreSQL、SQLAlchemy 2.x、Docker、passlib/bcrypt 或 argon2、PyJWT / python-jose。

AI 階段使用 LangChain 1.x 系列，建議：

```text
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langchain-ollama>=1.0,<2.0
```

實際版本需以當時 pip 可安裝且相容為準。

## 分層責任

### API Layer

`backend/app/api/` 只接收 request、驗證 schema、呼叫 service、回傳 response、管理 dependency。禁止直接操作 DB、直接呼叫 LLM/OCR、直接寫商業邏輯。

### Service Layer

`backend/app/services/` 處理 auth、refresh token、食材 CRUD、過期判斷、購物清單、AI 食譜、OCR 匯入、營養粗估。

### Domain Layer

`backend/app/domain/` 定義 Pydantic schema、SQLAlchemy model、enum、統一 response 格式。

### Infra Layer

`backend/app/infra/` 處理 DB、repository、settings、JWT/password hash、refresh token 儲存、LLM client、OCR client、檔案儲存。

## 建議目錄

```text
backend/app/api/{health,auth,pantry,expiration,shopping,recipes,ocr,nutrition}.py
backend/app/services/{auth_service,pantry_service,expiration_service,shopping_service,recipe_service,ocr_import_service,nutrition_service}.py
backend/app/domain/{schemas,models,enums}.py
backend/app/infra/{database,repository,settings,security,llm_client,ocr_client,storage}.py
```

## Auth 設計要求

- Access token 預設 15 分鐘。
- Refresh token 預設 7 天。
- refresh token 儲存在 DB，只存 token hash，不存明文 token。
- refresh token 必須支援撤銷與 logout。
- `refresh_tokens` 儲存 token_hash、user_id、expires_at、revoked_at、created_at、replaced_by_token_id。
- 前端自動 refresh 時，後端回傳新 access token；若採 rotation，也回傳新 refresh token。
- MVP 前端可使用 sessionStorage 儲存 token，但文件需標示 XSS 風險。
- 正式環境建議 refresh token 改用 httpOnly secure cookie。

## 圖片與檔案上傳要求

- 不把圖片 blob / base64 存 PostgreSQL。
- 開發階段可先存本機 `uploads/`。
- DB 只存 image_path / image_url。
- 上傳圖片大小限制預設 5MB。
- 可在上傳後壓縮、resize 或轉成較適合的格式。
- 正式環境使用 S3 / R2 / MinIO 等 object storage。

## 效能要求

- Repository 查詢不可一次讀取所有使用者資料。
- 列表 API 必須支援 page / page_size。
- Dashboard summary 避免 N+1 query。
- AI / OCR / 圖片處理 MVP 可同步呼叫；後續應可改為背景任務。
- Background job 可使用 Celery / RQ / Dramatiq。
- DB engine / session factory 集中管理，不可每次 request 重新建立 engine。
