import { FiSettings } from "react-icons/fi";

/** Settings 佔位頁（Phase 06-2）。 */
export function SettingsPage() {
  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiSettings aria-hidden="true" /> Settings（系統設定）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>此頁面將在後續階段提供主題、個人偏好與系統設定項目。</p>
    </section>
  );
}
