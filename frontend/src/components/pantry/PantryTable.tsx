import { FiEdit2, FiShoppingCart, FiTrash2 } from "react-icons/fi";

import { StatusBadge as CommonStatusBadge } from "../common/StatusBadge";
import type { PantryItem } from "../../features/pantry/pantryTypes";

interface PantryTableProps {
  items: PantryItem[];
  onEdit: (item: PantryItem) => void;
  onDelete: (item: PantryItem) => void;
  onAddToShopping: (item: PantryItem) => void;
}

/** Pantry 食材列表。 */
export function PantryTable({ items, onEdit, onDelete, onAddToShopping }: PantryTableProps) {
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
                <td data-label="食材名稱">{item.name}</td>
                <td data-label="分類">{item.category}</td>
                <td data-label="數量">{item.quantity}</td>
                <td data-label="單位">{item.unit}</td>
                <td data-label="保存位置">{item.storage_location || "-"}</td>
                <td data-label="過期日">{item.expiration_date || "-"}</td>
                <td data-label="狀態">
                  <StatusBadge status={item.status} />
                </td>
                <td className="pantry-table-actions-cell">
                  <div className="pantry-actions">
                    <button type="button" className="btn ghost pantry-action-btn" onClick={() => onAddToShopping(item)}>
                      <FiShoppingCart aria-hidden="true" /> 加入購物清單
                    </button>
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
    return <CommonStatusBadge label="已過期" tone="expired" />;
  }

  if (status === "expiring_soon") {
    return <CommonStatusBadge label="即將到期" tone="soon" />;
  }

  if (status === "normal") {
    return <CommonStatusBadge label="正常" tone="normal" />;
  }

  return <CommonStatusBadge label="未分類" tone="normal" />;
}
