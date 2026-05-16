import { FiAlertCircle, FiRepeat } from "react-icons/fi";

/** 藍新訂閱付款入口頁（Phase 14-5 待串接）。 */
export function BillingNewebpaySubscriptionPage() {
  return (
    <section className="card workspace-card billing-placeholder-page">
      <h2 className="workspace-title">
        <FiRepeat aria-hidden="true" /> 藍新訂閱付款
      </h2>
      <p>
        <FiAlertCircle aria-hidden="true" /> 這是 Phase 14-3 的占位頁，實際訂閱扣款流程將在 Phase 14-5 實作。
      </p>
    </section>
  );
}
