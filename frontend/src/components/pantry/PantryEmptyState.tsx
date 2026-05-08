import { FiArchive } from "react-icons/fi";

/** 食材空狀態提示。 */
export function PantryEmptyState() {
  return (
    <div className="pantry-empty card">
      <FiArchive aria-hidden="true" />
      <h3>目前還沒有食材</h3>
      <p>新增第一筆食材開始管理庫存</p>
    </div>
  );
}
