# Phase 14-0：Admin / Billing / Web Deployment 文件與架構方向調整

## 目標

建立 Phase 14 新主線的文件與架構方向，先明確規範 Admin、Billing、Web Deployment 邊界，不提前實作 14-1～14-6 runtime 功能。

## 本階段範圍

- 新增 Phase 14 子階段規劃（14-0～14-6）。
- 定義 Admin 權限方向、第一個 admin 帳號策略與空 DB 初始化策略。
- 定義 Billing 入口、付款模式切換與 one-time/subscription 分流規劃。
- 定義 Render + Vercel Web deployment baseline 與 AI server 暫不部署邊界。

## 非本階段範圍

- 不實作 admin runtime API / UI。
- 不實作 billing runtime API / UI / callback 驗證。
- 不修改 Phase 12 runtime。
- 不變更 Phase 13 定位。

## Phase 14 子階段規劃

1. Phase 14-0：文件與架構方向調整
2. Phase 14-1：Admin 權限與會員管理基礎
3. Phase 14-2：Web Deployment Baseline（Render + Vercel）
4. Phase 14-3：Billing 核心資料模型與 Upgrade 入口
5. Phase 14-4：藍新單次付款（one-time）
6. Phase 14-5：藍新訂閱制（subscription）
7. Phase 14-6：Admin Billing Management

## Admin 架構方向

### 前端與導覽

- 前端沿用既有 dashboard / sidebar 架構。
- 新增「會員管理」導航（僅 admin 可見），一般使用者不顯示。

### 權限與後端結構

- admin 權限最終必須由 DB 欄位控制（如 `role` 或 `is_admin`）。
- 不可只依賴前端顯示/隱藏判斷。
- backend admin API 不混入既有 `backend/app/api/`。
- 規劃使用獨立模組：`backend/app/admin_api/`。
- 仍維持既有分層：API -> Service -> Domain -> Infra。

## 第一個 Admin 帳號策略

### 既有帳號

- `admin@gmail.com` 規劃作為第一個既有 admin 帳號來源之一。

### 空 DB / 初始部署

- 需提供可執行的第一個 admin 建立方案，以下皆為可接受方向：
  - migration seed
  - init script
  - bootstrap command
  - 手動 SQL
  - 後台初始化流程
- 文件要求：需定義操作時機、冪等性、失敗處理與安全限制。
- Phase 14-0 僅文件規劃，不先實作上述 runtime 流程。

## Billing 架構方向

### 路由與模式

- 統一入口：`/billing/upgrade`
- 單次付款頁：`/billing/newebpay-one-time`
- 訂閱付款頁：`/billing/newebpay-subscription`
- 設定：`BILLING_MODE=one_time|subscription`
- `/billing/upgrade` 可依 `BILLING_MODE` 導向對應付款頁。

### 制度邊界

- one-time 與 subscription 為不同制度。
- 兩者需共用部分 billing 核心資料模型（如會員狀態、交易紀錄、provider event log）。
- Phase 14-0 僅規劃，不實作 runtime。

## 前端入口位置規劃（升級 PRO）

- 「升級 PRO」入口不放 Sidebar 主導航。
- 入口放在：`frontend/components/layout/UserMenu.tsx`。
- 順序規範：位於「Help」下方、「Log out」上方。
- 「Log out」維持最後一個選項。
- 後續若 `BILLING_MODE` 開啟，從此入口導向 `/billing/upgrade`。
- Phase 14-0 不修改 runtime UI。

## Deployment 方向

- 本輪 Web 先部署：
  - backend -> Render
  - frontend -> Vercel
- AI server / Ollama 暫不列入本輪免費雲端部署。
- 因金流 callback / notify 驗證需要公開網址，故先完成 Web deployment baseline。

## 與 Phase 13 邊界

- Phase 13 仍維持 AI Queue / Worker Scaling 規劃定位。
- 本階段不提前實作 Redis/RQ/queue migration。

## 本階段完成確認

- 已建立 Phase 14-0～14-6 文件化規劃。
- 已明確 Admin、Billing、Deployment 三條方向邊界。
- 已明確 `admin@gmail.com` 與空 DB 第一個 admin 初始化策略要求。
- 已明確 AI server 暫不列入本輪部署。
