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
- shopping 項目標記已購買後，前端可提示「是否加入或更新庫存？」。
- 在使用者確認 `name`、`category`、`quantity`、`unit`、`expiration_date`、`storage_location`、`note` 前，不可自動寫入 pantry。

## Slice 狀態設計

列表資料需包含 items、page、pageSize、total、loading、error。Auth 需包含 user、accessToken、isAuthenticated、loading、error。Theme mode 為 `light-soft | dark-soft`。
