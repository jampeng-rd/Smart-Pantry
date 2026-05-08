import { FiBookOpen } from "react-icons/fi";

/** Recipes 佔位頁（Phase 06-2）。 */
export function RecipesPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiBookOpen aria-hidden="true" /> Recipes（食譜建議）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段整合 AI 食譜建議與食材匹配提示。</p>
    </section>
  );
}
