# Phase 06-6A：Pantry / Shopping 前端整合 UX 修正

## 1. 階段目標

在不新增後端 API 的前提下，串接 Pantry 與 Shopping 前端流程，完成：
- Pantry 項目可加入購物清單。
- 已購買 Shopping 項目可經使用者確認後加入 Pantry。

## 2. 完成內容

### 2.0 路由與登入導向整理（Phase 06-6B）

- MVP 的登入後預設入口調整為 `/pantry`（食材庫存）。
- 登入成功後導向 `/pantry`（不再導向 `/dashboard`）。
- 註冊成功後導向 `/pantry`。
- 已登入使用者若進入首頁 `/`，會自動導向 `/pantry`。
- 未登入使用者進入受保護路由（包含 `/pantry`）仍會導回登入頁。
- Sidebar 保留「儀表板」入口，`/dashboard` 目前維持為 placeholder（未來總覽頁）。
- 已移除未使用的 `DashboardPlaceholderPage.tsx`（舊 Phase 06-1 佔位檔）。

### 2.1 Pantry -> Shopping：加入購物清單

- Pantry 列表操作區新增「加入購物清單」按鈕。
- 點擊後呼叫既有 `shoppingApi.create()`，payload 為：
  - `name`
  - `quantity`
  - `unit`
  - `source_pantry_item_id`
- 成功後顯示中文成功提示（不顯示 `source_pantry_item_id`）。
- 失敗時顯示中文錯誤卡片，不會中斷既有 Pantry CRUD 功能。

### 2.2 Shopping -> Pantry：加入庫存（需人工確認）

- Shopping 列表僅在 `is_purchased=true` 項目顯示「加入庫存」按鈕。
- 點擊後開啟 `ShoppingToPantryDrawer`（樣式沿用 `PantryFormDrawer`：`pantry-drawer` / `pantry-form`）。
- 預填欄位：
  - `name`
  - `quantity`
  - `unit`
- 使用者可確認/補齊欄位：
  - `category`
  - `expiration_date`
  - `storage_location`
  - `note`
- `category` 為前端必填，空白時顯示 `請輸入分類`，並阻擋送出 API。
- 表單送出時先呼叫既有 `pantryApi.create()` 新增 pantry item。
- 新增成功後自動呼叫既有 `shoppingApi.remove()`（透過 `deleteShoppingItem` thunk）移除原購物清單項目。
- 全程不會自動寫入 pantry，必須由使用者在 Drawer 按下確認。
- 成功/失敗皆提供中文提示。

## 3. 規則落實說明

- `source_pantry_item_id` 僅用於記錄 shopping 項目的來源關聯，不代表自動同步庫存。
- `source_pantry_item_id` 不在 UI 顯示 ID，僅作內部關聯。
- 標記已購買僅更新 shopping item 的 `is_purchased` / `purchased_at`。
- 已購買項目要加入 pantry，仍需人工確認資料後手動送出。
- 若 pantry item 刪除失敗（例如已被 shopping 引用），前端顯示友善中文提示：
  - `此食材已加入購物清單，請先刪除購物清單中的相關項目，再刪除此食材。`
- 本階段沒有新增任何後端 API。

## 4. 可及性與驗證

- 表單皆使用 `noValidate`，避免瀏覽器英文 tooltip。
- 保留 `aria-required`、`aria-invalid`、`aria-describedby`。
- icon-only button 皆有 `aria-label`（本階段新增的 icon 按鈕情境仍遵守）。
- Pantry 新增/編輯 Drawer 也已統一改為前端中文驗證，`category` 為必填，避免後端驗證錯誤直接顯示給使用者。

## 5. 受影響檔案

- `frontend/src/components/pantry/PantryTable.tsx`
- `frontend/src/pages/PantryPage.tsx`
- `frontend/src/components/shopping/ShoppingTable.tsx`
- `frontend/src/components/shopping/ShoppingToPantryDrawer.tsx`（新增）
- `frontend/src/pages/ShoppingPage.tsx`
- `frontend/src/styles/globals.css`
- `README.md`

## 6. 建置驗證

- 指令：`cd frontend && npm run build`
- 結果：通過（TypeScript + Vite build 成功）
