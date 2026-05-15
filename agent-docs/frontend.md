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

主題與狀態隔離規範：

- `recipes`、`ingredients`、`theme/settings` 為 user-scoped 狀態，不可跨帳號共用。
- 同一登入使用者切換頁面時，recipes/ingredients 可保留目前進度與結果。
- `logout`、切換帳號、auth 初始化失敗或 token 失效後，必須清空前一使用者的 recipes/ingredients 狀態。
- theme 若使用 localStorage，不可只用全域單一 key 直接覆蓋所有帳號偏好；登入後應以目前使用者 settings/theme 為準。
- 不可使用「component unmount 一律清空」做 ingredients 隔離，避免同一使用者切頁回來遺失進度。

## Redux 目錄規範

```text
frontend/src/app/{store,hooks}.ts
frontend/src/features/auth/{authSlice,authTypes}.ts
frontend/src/features/pantry/{pantrySlice,pantryTypes}.ts
frontend/src/features/expiration/{expirationSlice,expirationTypes}.ts
frontend/src/features/shopping/{shoppingSlice,shoppingTypes}.ts
frontend/src/features/recipes/{recipeSlice,recipeTypes}.ts
frontend/src/features/ingredients/{ingredientsSlice,ingredientsTypes}.ts
frontend/src/features/nutrition/{nutritionSlice,nutritionTypes}.ts
frontend/src/features/theme/{themeSlice,themeTypes}.ts
frontend/src/services/{apiClient,tokenService}.ts
```

`store.ts` 註冊 auth、pantry、expiration、shopping、recipes、ingredients、nutrition、theme。

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

## Forgot Password / Reset Password UI 規範（Phase 12-2）

- Login 頁需提供「忘記密碼」入口。
- 新增 Forgot Password view 與 Reset Password view。
- 視覺與互動需整合既有 Login/Register Auth Card 風格。
- UI 與錯誤訊息必須使用繁體中文。
- 不可顯示技術錯誤（例如 raw exception、HTTP stack、provider 錯誤細節）。
- Forgot Password 提交後，無論 email 是否存在都顯示相同成功提示。

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
- 食材辨識
- Nutrition route 可保留，但 MVP Sidebar 先隱藏（Nutrition 暫緩，避免未完成 placeholder）
- Dashboard route（`/dashboard`）目前保留為未來總覽頁，MVP 側欄可先隱藏該導航項目。
- Settings 由使用者選單進入。
- 未來 Phase 14-1 可新增「會員管理」導航，但僅 admin 可見。

### Sidebar 收合規範

- Sidebar 支援 expanded / collapsed。
- collapsed 時保留 icon。
- icon button 必須有 aria-label。

### 使用者選單規範

點擊 Sidebar 底部使用者區塊：

- 需在 Sidebar 內向上展開使用者選單。
- 不可超出 Sidebar 寬度。

至少包含：

- Profile（個人資料）
- Settings（系統設定）
- Help（說明）
- 升級 PRO（Phase 14 規劃）
- Log out

Phase 14 補充規劃：

- 「升級 PRO」入口不放 Sidebar 主導航。
- 入口位置固定在 `frontend/components/layout/UserMenu.tsx`。
- 顯示順序：`Help` 下方、`Log out` 上方。
- `Log out` 維持最後一個選項。
- 後續若 `BILLING_MODE` 開啟，從此入口導向 `/billing/upgrade`。
- Phase 14-0 僅文件規劃，不先修改 runtime UI。

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

## AI 功能前端完成標準（Phase 08～12）

Recipes、食材辨識頁不可只保留 placeholder。Nutrition 暫緩，未進入對應階段前不可新增未完成 placeholder。

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
- recipes 狀態為 user-scoped：同一使用者切頁可保留；帳號切換或 auth 失效時必須 reset。

食材辨識 UI：

- ingredient photo upload
- 食材辨識 candidate items
- 使用者確認後寫入 pantry
- ingredients 狀態為 user-scoped：preview / 檔名 / candidates / job status / polling / 確認表單在同一使用者切頁可保留；帳號切換或 auth 失效時必須 reset。

Nutrition UI（未來恢復後）：

- nutrition estimate result
- AI 生活參考聲明


## Profile / Settings / Help 頁面規範（Phase 10-1 已實作）

### Profile（個人資料）

Profile 是帳號本身資料：

- 使用者名稱可修改。
- Email 不可修改。
- 頭像若未上傳圖片，顯示 display_name 第一個字元；例如 `YG` 顯示 `Y`，`小明` 顯示 `小`。
- 提供修改密碼入口。

### Settings（系統設定）

Settings 是系統行為偏好。頁面區塊建議順序：

1. 外觀設定：主題切換放第一個區塊。
2. 到期 Email 提醒：選項順序為「不提醒」、「前 1 天（預設）」、「前 3 天」。
3. 時區：預設瀏覽器時區，未來可讓使用者指定。
4. 語言：MVP 固定繁體中文，保留欄位。
5. 登出所有裝置：未來功能。
6. 最近登入時間：未來功能。

### Help（說明）

Help 應包含：基本操作教學、AI 食譜限制、食材辨識拍攝建議、Email 提醒規則與 FAQ。Help 文字需使用繁體中文，並避免過度技術化。


Phase 10-1 已完成重點：

- Profile：可讀取/更新 display_name、顯示不可修改 Email、密碼顯示/隱藏與修改密碼。
- Settings：第一區塊為主題切換，並與 themeSlice 同步；可儲存 theme/timezone/expiration_email_reminder_days。
- 到期提醒選項順序固定：不提醒、前 1 天（預設）、前 3 天。
- Help：完成繁體中文教學、AI/Vision 使用限制、Email 提醒規則與 FAQ。

## Phase 10-3：Settings 寄送紀錄 UI（已完成）

- Settings「到期 Email 提醒」區塊下方新增「最近寄送紀錄」。
- 顯示欄位：排程日期、寄送時段、提醒天數、食材數量、收件 Email、狀態、寄送時間、錯誤訊息（failed 才顯示）。
- 狀態對應：
  - `success` -> 成功
  - `failed` -> 失敗
  - `pending` -> 處理中
- 寄送時段對應：
  - `morning_08` -> 上午 8:00
  - `evening_17` -> 下午 5:00
- 提醒天數對應：
  - `1` -> 前 1 天
  - `3` -> 前 3 天
  - `none` -> 不提醒
- UI 狀態需涵蓋 loading、error + 重試、empty state。
- 分頁先固定每頁 10 筆，並使用共用 `Pagination` 元件，不自行手刻分頁按鈕。
- RWD：桌機 table；手機 card-like，避免嚴重橫向捲動。
- Help FAQ 補充可查看寄送紀錄位置，並註明目前為 fake email client。
- 手機版 card 必須顯示：排程日期、寄送時段、提醒天數、食材數量、收件 Email、狀態、寄送時間、錯誤訊息（若有）。
- 補充說明寄送紀錄只保留 7 天，且於每天上午 8:00 runner 時清理超過 7 天紀錄。

## Phase 11-4 Email Delivery UX 規範

- 前端不得直接顯示 provider 原始錯誤（HTTP status、API key/domain/from 欄位錯誤、SMTP exception、traceback）。
- Settings 寄送紀錄只使用後端 `user_friendly_error_message`。
- 前端網路連線問題（`NetworkError` / `Failed to fetch` / browser network failure）統一顯示：`網路異常，請稍後再試。`
- 前端不可自行用 provider keyword 硬編碼映射。

## Phase 11-4 錯誤訊息四分類

- 前端只顯示後端 `user_friendly_error_message` 與統一網路錯誤文案。
- 禁止顯示 provider 原始錯誤、HTTP status、API key/domain/from/sender 錯誤字串。
- backend 500 或系統異常情境應顯示：`目前系統偵測異常，系統維修中。`
