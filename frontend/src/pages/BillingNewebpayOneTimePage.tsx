import { FiAlertCircle, FiCreditCard } from "react-icons/fi";

/** 藍新單次付款入口頁（Phase 14-4 待串接）。 */
export function BillingNewebpayOneTimePage() {
  return (
    <section className="card workspace-card billing-placeholder-page">
      <h2 className="workspace-title">
        <FiCreditCard aria-hidden="true" /> 藍新單次付款
      </h2>
      <p>
        <FiAlertCircle aria-hidden="true" /> 這是 Phase 14-3 的占位頁，實際付款流程將在 Phase 14-4 實作。
      </p>
    </section>
  );
}
