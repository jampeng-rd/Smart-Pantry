import { FiCheckCircle, FiEdit2, FiRotateCcw, FiTrash2 } from "react-icons/fi";

import type { ShoppingItem } from "../../features/shopping/shoppingTypes";

interface ShoppingTableProps {
  items: ShoppingItem[];
  onEdit: (item: ShoppingItem) => void;
  onDelete: (item: ShoppingItem) => void;
  onTogglePurchased: (item: ShoppingItem) => void;
}

/** Shopping 購物清單列表。 */
export function ShoppingTable({ items, onEdit, onDelete, onTogglePurchased }: ShoppingTableProps) {
  return (
    <div className="card shopping-table-card">
      <div className="shopping-table-wrap">
        <table className="shopping-table">
          <thead>
            <tr>
              <th>名稱</th>
              <th>數量</th>
              <th>單位</th>
              <th>狀態</th>
              <th>購買時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td data-label="名稱">{item.name}</td>
                <td data-label="數量">{item.quantity}</td>
                <td data-label="單位">{item.unit || "-"}</td>
                <td data-label="狀態">
                  {item.is_purchased ? (
                    <span className="pantry-status pantry-status-normal">
                      <FiCheckCircle aria-hidden="true" /> 已購買
                    </span>
                  ) : (
                    <span className="pantry-status pantry-status-soon">未購買</span>
                  )}
                </td>
                <td data-label="購買時間">{item.purchased_at || "-"}</td>
                <td className="shopping-table-actions-cell">
                  <div className="shopping-actions">
                    <button type="button" className="btn ghost shopping-action-btn" onClick={() => onTogglePurchased(item)}>
                      {item.is_purchased ? <FiRotateCcw aria-hidden="true" /> : <FiCheckCircle aria-hidden="true" />}
                      {item.is_purchased ? "設為未購買" : "標記已購買"}
                    </button>
                    <button type="button" className="btn ghost shopping-action-btn" onClick={() => onEdit(item)}>
                      <FiEdit2 aria-hidden="true" /> 編輯
                    </button>
                    <button type="button" className="btn ghost shopping-action-btn shopping-danger-btn" onClick={() => onDelete(item)}>
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
