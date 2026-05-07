# Phase 06-1：Auth UI + Protected Layout

## 1. 階段目標

完成前端登入/註冊流程、token 管理、受保護路由與登入後基本版型。未登入使用者不可進入 Dashboard，登入成功後導向 Dashboard placeholder。

## 2. 完成內容

- 新增 `LoginPage`。
- 新增 `RegisterPage`。
- 新增 `DashboardPlaceholderPage`。
- 新增 `ProtectedRoute`（auth guard）。
- 新增 `ProtectedLayout`（登入後簡化左側區塊 + 使用者設定區）。
- 完整實作 `authSlice`：
  - `initializeAuth`
  - `login`
  - `register`
  - `logout`
  - `loading/error/initialized` 狀態
- 完整實作 `tokenService`：
  - token 讀寫集中管理
  - access token 即將過期判斷
  - token 清除
- 完整實作 `apiClient` Auth 串接：
  - `register`
  - `login`
  - `refresh`
  - `logout`
  - `me`
- API 授權請求流程：
  - access token 快過期先 refresh
  - API 回 401 最多 refresh 一次並重送
  - refresh 失敗才清除登入狀態
- Login / Register 改為互斥顯示，不同時渲染。
- 修正 `initializeAuth` 與 `login/register` 競態覆蓋：
  - `login.fulfilled` / `register.fulfilled` 會設定 `initialized=true`
  - `initializeAuth` 完成或失敗時，不覆蓋已登入狀態
- 主題與樣式修正：
  - 預設主題 `light-soft`
  - `dark-soft` 背景不使用漸層
  - button `border-radius` 統一約 `10px`
  - 主題切換移到登入後使用者設定區
- 首頁 Auth UI 調整：
  - Login / Register 僅保留乾淨單一卡片
  - 系統名稱與英文副標題放在 auth card 內最上方
  - 移除首頁「請先登入以進入 Dashboard」與主題切換
  - 表單標題使用純文字「登入」/「建立帳號」，不使用 icon 標題
  - 密碼欄位新增顯示/隱藏按鈕（登入、註冊、確認密碼）
  - auth layout 採 `min-height: 100vh` 置中（桌機/手機）

## 3. 涉及檔案

- `frontend/src/App.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/src/components/ProtectedLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/pages/DashboardPlaceholderPage.tsx`
- `frontend/src/features/auth/authSlice.ts`
- `frontend/src/features/auth/authTypes.ts`
- `frontend/src/services/tokenService.ts`
- `frontend/src/services/apiClient.ts`
- `frontend/src/styles/globals.css`
- `README.md`
- `docs/phase-06-1-auth-ui.md`

## 4. 如何啟動前端

```bash
cd frontend
npm install
npm run dev
```

## 5. 如何測試 Login/Register

1. 啟動 backend（`http://localhost:8000`）。
2. 啟動 frontend。
3. 開啟 `/`：應看到登入畫面。
4. 點選「沒有帳號？前往註冊」，完成註冊。
5. 註冊成功後應自動登入並導向 `/dashboard`。
6. 重新整理 `/dashboard`：應嘗試恢復登入狀態。
7. 點擊登出：應清除 token 並回 `/`。
8. 未登入直接開 `/dashboard`：應被導回 `/`。

## 6. tokenService 設計

- 集中管理 `sessionStorage`：
  - `getAccessToken`
  - `getRefreshToken`
  - `saveTokens`
  - `clearTokens`
- 使用 JWT `exp` 判斷 access token 是否快過期（預設緩衝 60 秒）。
- 元件不可直接操作 `sessionStorage`，避免 token 邏輯分散。

## 7. route guard 設計

- `ProtectedRoute` 負責檢查 `initialized` 與 `isAuthenticated`。
- 若已初始化但未登入，執行導回 `/`。
- `/dashboard` 必須包在 `ProtectedRoute` 內。
- `/` 為登入/註冊入口，登入成功導向 `/dashboard`。
- Auth 首頁僅顯示單一畫面：`login` 或 `register`，不會同時顯示兩頁。

## 7.1 initializeAuth 競態修正

- App mount 會觸發 `initializeAuth`，但不再覆蓋後續使用者手動登入成功狀態。
- 若 `initializeAuth` 回來時已登入，保持 `isAuthenticated=true` 與既有 `user`。
- 避免初始化流程把登入成功狀態誤改回未登入。

## 8. sessionStorage 安全限制

- MVP 可用 `sessionStorage` 儲存 token，但有 XSS 風險。
- 若前端被注入惡意腳本，token 可能被讀取。
- 正式環境建議改為 `httpOnly secure cookie` 儲存 refresh token，並搭配 CSRF 防護策略。

## 9. 已知限制

- 目前 Dashboard 僅 placeholder，未實作完整 Sidebar 與功能頁。
- 本階段未實作 Pantry / Expiration / Shopping 的前端操作頁。
- 目前使用簡易 pathname 路由，後續可評估導入正式 router。
- 尚未加入前端自動化測試（目前以 build 與手動流程驗證）。

## 10. 下一階段建議

- 進入 Phase 06-2：實作 Pantry / Expiration / Shopping 頁面與狀態管理。
- 增加 auth 相關前端測試（tokenService、guard、401 重試流程）。
- 補 `user_preferences.timezone` 設定與時間顯示偏好整合。
