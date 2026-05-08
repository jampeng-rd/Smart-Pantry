import { FiHome } from "react-icons/fi";

import { useAppSelector } from "../app/hooks";

/** Dashboard 佔位頁（Phase 06-2）。 */
export function DashboardPage() {
  const user = useAppSelector((state) => state.auth.user);

  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiHome aria-hidden="true" /> Dashboard（儀表板）
      </h2>
      <p className="workspace-phase">Phase 06-2 Placeholder</p>
      <p>你好，{user?.display_name ?? "使用者"}。此頁面將顯示庫存摘要、到期提醒與快捷操作。</p>
    </section>
  );
}
