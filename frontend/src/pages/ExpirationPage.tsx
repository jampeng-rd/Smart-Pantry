import { FiClock } from "react-icons/fi";

/** Expiration 佔位頁（Phase 06-2）。 */
export function ExpirationPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiClock aria-hidden="true" /> Expiration（到期提醒）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段實作到期日狀態分類、到期提醒與摘要視圖。</p>
    </section>
  );
}
