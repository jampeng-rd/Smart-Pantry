import { FiLayout, FiShield } from "react-icons/fi";

import { useAppSelector } from "../app/hooks";

/** Dashboard 佔位頁（Phase 06-1）。 */
export function DashboardPlaceholderPage() {
  const user = useAppSelector((state) => state.auth.user);

  return (
    <section className="card">
      <h2>
        <FiLayout aria-hidden="true" /> Dashboard Placeholder
      </h2>
      <p>
        你好，{user?.display_name ?? "使用者"}。目前僅完成 Auth UI 與受保護版型，Pantry / Expiration / Shopping 等功能頁將在後續階段實作。
      </p>
      <p className="muted-text">
        <FiShield aria-hidden="true" /> 僅登入使用者可看到此頁。
      </p>
    </section>
  );
}
