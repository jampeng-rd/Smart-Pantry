import { FiEdit2, FiTrash2 } from "react-icons/fi";

import type { PantryItem } from "../../features/pantry/pantryTypes";

interface PantryTableProps {
  items: PantryItem[];
  onEdit: (item: PantryItem) => void;
  onDelete: (item: PantryItem) => void;
}

/** Pantry 食材列表。 */
export function PantryTable({ items, onEdit, onDelete }: PantryTableProps) {
  return (
    <div className="card pantry-table-card">
      <div className="pantry-table-wrap">
        <table className="pantry-table">
          <thead>
            <tr>
              <th>食材名稱</th>
              <th>分類</th>
              <th>數量</th>
              <th>單位</th>
              <th>保存位置</th>
              <th>過期日</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.category}</td>
                <td>{item.quantity}</td>
                <td>{item.unit}</td>
                <td>{item.storage_location || "-"}</td>
                <td>{item.expiration_date || "-"}</td>
                <td>
                  <StatusBadge status={item.status} />
                </td>
                <td>
                  <div className="pantry-actions">
                    <button type="button" className="btn ghost pantry-action-btn" onClick={() => onEdit(item)}>
                      <FiEdit2 aria-hidden="true" /> 編輯
                    </button>
                    <button type="button" className="btn ghost pantry-action-btn pantry-danger-btn" onClick={() => onDelete(item)}>
                      <FiTrash2 aria-hidden="true" /> 刪除
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: PantryItem["status"] }) {
  if (status === "expired") {
    return <span className="pantry-status pantry-status-expired">已過期</span>;
  }

  if (status === "expiring_soon") {
    return <span className="pantry-status pantry-status-soon">即將到期</span>;
  }

  if (status === "normal") {
    return <span className="pantry-status pantry-status-normal">正常</span>;
  }

  return <span className="pantry-status">未分類</span>;
}
