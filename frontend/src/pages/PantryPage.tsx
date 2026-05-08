import { FiArchive } from "react-icons/fi";

/** Pantry 佔位頁（Phase 06-2）。 */
export function PantryPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiArchive aria-hidden="true" /> Pantry（食材庫存）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段實作食材庫存列表、篩選與新增/編輯流程。</p>
    </section>
  );
}
