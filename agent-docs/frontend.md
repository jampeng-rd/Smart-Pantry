# Web Frontend 規範

## 技術棧

React、Vite、TypeScript、Redux Toolkit、React Redux、react-icons、CSS variables / CSS Modules / Tailwind CSS。

## UI 語言與 Icon 規範

- UI 主要語言必須是繁體中文。
- 按鈕需優先使用 `react-icons`。
- 只有 icon 的按鈕必須有 `aria-label`。
- 列表選項、導覽、篩選按鈕使用「icon + 繁體中文」。
- 不可整個 UI 只有 icon 而沒有文字提示。

範例：

```tsx
<button aria-label="新增食材"><FiPlus /></button>
<button><FiShoppingCart />加入購物清單</button>
```

## 主題規範

支援兩種主題：

- `light-soft`：柔和亮色，主背景不可純白。
- `dark-soft`：柔和暗色，主背景不可純黑。

建議 CSS variables：

```css
:root[data-theme="light-soft"] { --color-bg:#f7f3ea; --color-surface:#fffaf0; --color-text:#26312b; }
:root[data-theme="dark-soft"] { --color-bg:#171a1c; --color-surface:#222826; --color-text:#edf2ed; }
```

主題切換由 `themeSlice.ts` 管理，主題偏好可持久化到 localStorage。Token 不建議放 localStorage。

## Redux 目錄規範

```text
frontend/src/app/{store,hooks}.ts
frontend/src/features/auth/{authSlice,authTypes}.ts
frontend/src/features/pantry/{pantrySlice,pantryTypes}.ts
frontend/src/features/expiration/{expirationSlice,expirationTypes}.ts
frontend/src/features/shopping/{shoppingSlice,shoppingTypes}.ts
frontend/src/features/recipes/{recipeSlice,recipeTypes}.ts
frontend/src/features/ocr/{ocrSlice,ocrTypes}.ts
frontend/src/features/nutrition/{nutritionSlice,nutritionTypes}.ts
frontend/src/features/theme/{themeSlice,themeTypes}.ts
frontend/src/services/{apiClient,tokenService}.ts
```

`store.ts` 註冊 auth、pantry、expiration、shopping、recipes、ocr、nutrition、theme。

`hooks.ts` 使用 React Redux v9 typed hooks：

```ts
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
```

## API 與 Refresh Token 規範

- 元件不可直接呼叫 fetch。
- API 呼叫集中在 `services/apiClient.ts`。
- Token 讀寫與 refresh 集中在 `services/tokenService.ts` 或 auth feature。
- MVP 前端可使用 sessionStorage 儲存 access token / refresh token。
- sessionStorage 關閉分頁後會清除，但仍有 XSS 風險，文件需標示安全限制。
- 正式環境建議 refresh token 改用 httpOnly secure cookie。
- request 前檢查 access token 是否快過期。
- 若快過期，先呼叫 `/auth/refresh`。
- 若 API 回傳 401，最多 refresh 一次並重送原 request。
- Refresh 失敗才清除登入狀態並導回登入頁。

## 時間顯示規範

- 後端與 API 以 UTC 為標準時間，前端不可假設回傳時間是本地時間。
- Phase 06 MVP 先用瀏覽器 `Intl API` 將 UTC datetime 轉為使用者本機時區顯示。
- 後續可支援 `user_preferences.timezone` 覆蓋瀏覽器時區。
- 需可正確顯示台灣（`Asia/Taipei`）、美國（`America/*`）、日本（`Asia/Tokyo`）、英國（`Europe/London`）等本地時間。

## Shopping 與 Pantry UX 規範

- `shopping_list_items` 與 `pantry_items` 是不同資料集合。
- `source_pantry_item_id` 只作內部來源關聯，不在 UI 顯示 ID。
- 從 Pantry 加入 Shopping 時，前端建立 shopping item 並帶入 `source_pantry_item_id`。
- shopping 項目標記已購買只更新 `is_purchased` / `purchased_at`。
- 在使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note` 前，不可自動寫入 pantry。
- 已購買項目確認加入 pantry 成功後，前端自動移除原 shopping item（使用既有 `pantryApi.create()` + `shoppingApi.remove()`）。

## 表單驗證與錯誤訊息規範

- Pantry 新增/編輯：
  - `name` 必填
  - `category` 必填
  - `quantity` 必填，且必須是整數且 `>= 1`
- Shopping 新增/編輯：
  - `name` 必填
  - `quantity` 必填，且必須是整數且 `>= 1`
- Shopping -> Pantry 加入庫存：
  - `category` 必填
- 所有表單使用 `noValidate` + 自訂繁中錯誤訊息，不依賴瀏覽器英文 tooltip。
- 不直接向使用者顯示 Pydantic 原始錯誤、NetworkError 或 fetch error。

## Slice 狀態設計

列表資料需包含 items、page、pageSize、total、loading、error。Auth 需包含 user、accessToken、isAuthenticated、loading、error。Theme mode 為 `light-soft | dark-soft`。

## Dashboard Layout 規範

### App Layout

登入前：
- 首頁顯示登入 / 註冊頁。
- 未登入不可直接進入任何受保護頁。

登入後：
- 使用 Dashboard Layout。
- MVP 預設導向 `/pantry`（不是 `/dashboard`）。
- 採 Sidebar + Workspace 結構。

建議結構：

```text
<AppLayout>
  <Sidebar />
  <MainLayout>
    <TopToolbar />
    <Workspace />
  </MainLayout>
</AppLayout>
```

### Sidebar 規範

Sidebar 必須包含：
- Logo 區。
- Sidebar 收合按鈕。
- 功能導覽。
- 底部固定使用者資訊區。

Sidebar 功能導覽至少包含：
- Pantry
- Expiration
- Shopping
- Recipes
- OCR
- Nutrition
- Dashboard route（`/dashboard`）目前保留為未來總覽頁，MVP 側欄可先隱藏該導航項目。
- Settings 由使用者選單進入。

### Sidebar 收合規範

- Sidebar 支援 expanded / collapsed。
- collapsed 時保留 icon。
- icon button 必須有 aria-label。

### 使用者選單規範

點擊 Sidebar 底部使用者區塊：
- 需在 Sidebar 內向上展開使用者選單。
- 不可超出 Sidebar 寬度。

至少包含：
- Profile
- Settings
- Help
- Log out

### Workspace 規範

- Workspace 為主要內容區。
- 每個頁面最上方需有 Toolbar。

Toolbar 可包含：
- 搜尋
- 篩選
- 排序
- 新增按鈕
- 頁面操作

## 前端階段拆分規範

Phase 06 必須拆分：

### Phase 06-1
- Login/Register UI
- tokenService
- route guard
- protected layout

### Phase 06-2
- Sidebar
- Dashboard layout
- theme switch
- responsive layout

### Phase 06-3
- Pantry UI
- pantry CRUD
- pagination
- filter/sort/search

### Phase 06-4
- Expiration UI
- expiration summary
- status UI

### Phase 06-5
- Shopping UI
- purchase state
- shopping/pantry UX

### Phase 06-6
- UX polish
- loading/error states
- timezone display
- responsive fixes
- 路由整理（登入/註冊/已登入首頁導向 `/pantry`）


## AI 功能前端完成標準（Phase 08～11）

Recipes、OCR、Nutrition 頁不可只保留 placeholder。進行對應 AI 階段時，必須完成實際 UI 與 backend job API 串接。

AI job frontend 共通流程：
1. frontend 呼叫 backend 建立 job
2. 顯示 pending/running
3. 前端 polling backend job status
4. success 後顯示 result
5. failed 後顯示中文友善錯誤
6. component unmount 時停止 polling
7. frontend 不可直接呼叫 ai_server

Recipes UI：
- selected_items
- auto_from_pantry
- recipe result UI
- cooking tools / allergies / diet preference

OCR UI：
- receipt upload
- OCR candidate items
- 使用者確認後寫入 pantry

Nutrition UI：
- nutrition estimate result
- AI 生活參考聲明
