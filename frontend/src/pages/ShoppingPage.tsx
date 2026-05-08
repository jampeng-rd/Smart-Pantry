import { FiShoppingCart } from "react-icons/fi";

/** Shopping 佔位頁（Phase 06-2）。 */
export function ShoppingPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiShoppingCart aria-hidden="true" /> Shopping（購物清單）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段實作購物清單檢視、標記已購買與來源追蹤。</p>
    </section>
  );
}
