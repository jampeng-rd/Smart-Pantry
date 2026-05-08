import { FiInbox } from "react-icons/fi";

interface ExpirationEmptyStateProps {
  message: string;
}

/** 到期提醒空狀態。 */
export function ExpirationEmptyState({ message }: ExpirationEmptyStateProps) {
  return (
    <section className="card expiration-empty">
      <FiInbox aria-hidden="true" />
      <h3>{message}</h3>
      <p>你可以先前往「食材庫存」新增食材後再回來查看狀態。</p>
    </section>
  );
}
