import { FiCamera } from "react-icons/fi";

/** OCR 佔位頁（Phase 06-2）。 */
export function OCRPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiCamera aria-hidden="true" /> OCR（票據匯入）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段提供發票/收據匯入與候選結果確認流程。</p>
    </section>
  );
}
