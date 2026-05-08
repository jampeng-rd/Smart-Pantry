import { FiAlertTriangle, FiCheckCircle, FiClock } from "react-icons/fi";

import type { ExpirationItem } from "../../features/expiration/expirationTypes";

interface ExpirationItemListProps {
  items: ExpirationItem[];
}

/** 到期提醒清單。 */
export function ExpirationItemList({ items }: ExpirationItemListProps) {
  return (
    <section className="card expiration-list-card" aria-label="到期提醒清單">
      <div className="expiration-table-wrap">
        <table className="expiration-table">
          <thead>
            <tr>
              <th>食材名稱</th>
              <th>分類</th>
              <th>數量</th>
              <th>保存位置</th>
              <th>過期日</th>
              <th>狀態</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td data-label="食材名稱">{item.name}</td>
                <td data-label="分類">{item.category}</td>
                <td data-label="數量">
                  {item.quantity} {item.unit}
                </td>
                <td data-label="保存位置">{item.storage_location || "-"}</td>
                <td data-label="過期日">{item.expiration_date || "-"}</td>
                <td data-label="狀態">
                  <ExpirationStatusBadge status={item.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ExpirationStatusBadge({ status }: { status: ExpirationItem["status"] }) {
  if (status === "expired") {
    return (
      <span className="pantry-status pantry-status-expired">
        <FiAlertTriangle aria-hidden="true" /> 已過期
      </span>
    );
  }

  if (status === "expiring_soon") {
    return (
      <span className="pantry-status pantry-status-soon">
        <FiClock aria-hidden="true" /> 即將到期
      </span>
    );
  }

  return (
    <span className="pantry-status pantry-status-normal">
      <FiCheckCircle aria-hidden="true" /> 正常
    </span>
  );
}
