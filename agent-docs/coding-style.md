# Coding Style 規範

## Python

- 使用 type hints。
- 所有函式、類別、重要方法都要有繁體中文 docstring。
- 函式保持小而明確。
- 不要在 API route 寫商業邏輯。
- 不同功能要分開檔案。
- Auth token、password hash、security helper 放在 infra/security.py 或獨立 security 模組。

## TypeScript / React

- 使用 TypeScript。
- Redux slice 命名清楚。
- API 型別集中管理。
- 元件只處理畫面，不直接寫 API。
- 複雜邏輯抽到 hooks、service 或 slice thunk。
- 不同功能分開 features。
- 不使用 `any` 逃避型別錯誤。
- UI 文字以繁體中文為主。
- 按鈕與選單使用 `react-icons`，導覽與列表選項採 icon + 繁體中文。
- 主題色彩使用 CSS variables，不要在元件內散落硬編碼顏色。

## Commit Message

```text
feat(auth): add refresh token flow
test(pantry): add pantry service unit tests
docs: update phase 03 pantry document
fix(expiration): handle expired item status
ci: add backend and frontend build checks
```


## Security / Storage Style

- 前端 MVP token 讀寫集中在 tokenService，不可散落在元件中直接操作 sessionStorage。
- 不可在程式中將圖片轉 base64 後寫入 PostgreSQL。
- 圖片上傳、壓縮、resize、儲存路徑產生應封裝在 infra/storage.py 或前端對應工具函式中。
