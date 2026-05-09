import { FiArchive } from "react-icons/fi";
import { EmptyState } from "../common/EmptyState";

/** 食材空狀態提示。 */
export function PantryEmptyState() {
  return (
    <EmptyState
      as="div"
      className="pantry-empty card"
      icon={FiArchive}
      title="目前還沒有食材"
      description="新增第一筆食材開始管理庫存"
    />
  );
}
