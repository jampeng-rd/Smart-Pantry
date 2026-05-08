import { FiInbox } from "react-icons/fi";

interface ExpirationEmptyStateProps {
  statusLabel: string;
}

/** 到期提醒空狀態。 */
export function ExpirationEmptyState({ statusLabel }: ExpirationEmptyStateProps) {
  return (
    <section className="card expiration-empty">
      <FiInbox aria-hidden="true" />
      <h3>目前沒有符合條件的食材</h3>
      <p>{statusLabel}暫時沒有需要顯示的到期提醒。</p>
    </section>
  );
}
