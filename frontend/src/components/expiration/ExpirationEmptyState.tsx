import { FiInbox } from "react-icons/fi";
import { EmptyState } from "../common/EmptyState";

interface ExpirationEmptyStateProps {
  message: string;
}

/** 到期提醒空狀態。 */
export function ExpirationEmptyState({ message }: ExpirationEmptyStateProps) {
  return (
    <EmptyState
      as="section"
      className="card expiration-empty"
      icon={FiInbox}
      title={message}
      description="你可以先前往「食材庫存」新增食材後再回來查看狀態。"
    />
  );
}
