# Phase 06-2：Dashboard + Sidebar + Theme

## 1. 階段目標

本階段聚焦完成 Dashboard 系統版型與導覽骨架，不進入 Pantry / Expiration / Shopping / Recipes / OCR / Nutrition 的 CRUD 功能。

## 2. Dashboard Layout

已建立正式版型：

- `AppLayout`
- `Sidebar`
- `TopToolbar`
- `Workspace`

結構如下：

- `<AppLayout>`
- `<Sidebar />`
- `<MainLayout>`
- `<TopToolbar />`
- `<Workspace />`

## 3. Sidebar

### 3.1 Logo 區

- 展開狀態使用較短品牌文案：`智慧食材系統` / `Smart Pantry`
- 收合狀態改為僅顯示主題對應 logo（不顯示文字），logo 縮小為約 38px
- 收合狀態 header 預設顯示 logo，滑鼠 hover/focus 才顯示「展開側邊欄」按鈕
  - `light-soft`：`light_soft_logo.png`
  - `dark-soft`：`Dark_Soft_logo.png`
- 右側提供收合按鈕（icon button，具完整 `aria-label`）
- 修正收合後 brand 區高度，避免 nav 圖示被過大空白往下推
- 修正收合狀態 header 內按鈕位置，避免壓在側欄邊線上

### 3.2 導覽區

導覽項目（icon + 繁體中文文字）：

- Pantry（食材庫存）
- Expiration（到期提醒）
- Shopping（購物清單）
- Recipes（食譜建議）
- OCR（OCR 匯入）
- Nutrition（營養估算）

補充（Phase 06-6B / 後續 UX 整理）：
- `/dashboard` route 保留為未來總覽頁 placeholder。
- MVP Sidebar 導航暫時隱藏「儀表板」項目，待總覽實作後再重新啟用。

目前採用既有輕量 `pathname` routing，不引入 `react-router-dom`。
`/settings` 路由仍保留，供 user menu 入口使用。

### 3.3 使用者區 + User Menu

Sidebar 底部顯示：

- `display_name`
- （預留）`PRO` badge：僅當 `subscription_tier === "PRO"` 時顯示

點擊後在 Sidebar 內向上展開選單，包含：

- Profile
- Settings
- Help
- Theme Toggle
- Log out

- 一般狀態：選單在 Sidebar 內向上展開。
- 收合狀態（desktop）：選單改為 Sidebar 內 icon-only menu（不顯示文字），每項為方形 icon button。
- 修正收合 icon-only user menu 的 x 軸 overflow，避免出現 horizontal scrollbar。

## 4. Responsive Drawer

- Desktop（>1024px）：Sidebar 固定左側，支援 expanded/collapsed（約 260px / 84px）。
- Tablet/Mobile（<=1024px）：Sidebar 轉為 overlay drawer。
- 開啟 drawer 時會顯示背景 overlay。
- 開啟 drawer 時鎖定 `body` 捲動（`overflow: hidden`），避免版面穿透與橫向捲動問題。
- Mobile toolbar 顯示 hamburger button，並提供完整 `aria-label`。

## 5. Theme Integration

已全面套用 theme token：

- Sidebar：`var(--color-surface)` + `var(--color-border)`
- Nav hover：`var(--color-surface-hover)`
- Nav active：以 accent 色系混合顯示
- Card/Button/Input/Toolbar/Divider：全面改為 CSS variables
- Transition：使用 `var(--transition-fast)` / `var(--transition-normal)`

## 6. Placeholder Pages

新增以下頁面骨架（統一卡片風格）：

- `DashboardPage`
- `PantryPage`
- `ExpirationPage`
- `ShoppingPage`
- `RecipesPage`
- `OCRPage`
- `NutritionPage`
- `SettingsPage`

每頁包含：

- 頁面名稱
- `Phase 06-2 Placeholder`
- 後續功能說明

## 7. Responsive Strategy

- 版型採用 CSS Grid。
- Desktop 保持 sidebar + workspace 雙欄。
- Mobile 採 drawer + overlay 模式，toolbar 改為上下堆疊。
- 全域持續維持 `overflow-x: hidden`，避免多餘水平捲軸。
- Toolbar 右側 action 改為 icon-only more button（`aria-label="更多頁面操作"`），並與搜尋框高度對齊（40px）。
- 收合 sidebar 的 nav/user/menu 全部改為方形 icon button（40x40）避免 hover/active 框外溢。

## 8. 涉及檔案

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/TopToolbar.tsx`
- `frontend/src/components/layout/UserMenu.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/PantryPage.tsx`
- `frontend/src/pages/ExpirationPage.tsx`
- `frontend/src/pages/ShoppingPage.tsx`
- `frontend/src/pages/RecipesPage.tsx`
- `frontend/src/pages/OCRPage.tsx`
- `frontend/src/pages/NutritionPage.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/styles/globals.css`
- `docs/phase-06-2-dashboard-layout.md`
- `README.md`

## 9. 已知限制

- 目前功能頁仍為 placeholder，尚未串接各 feature slice 的 CRUD。
- 目前路由採用 pathname 手動切換，後續可再評估導入正式 router。
- User menu 的 Profile / Settings / Help 目前導向設定頁佔位，尚未拆分獨立頁。
