import { FiShoppingCart } from "react-icons/fi";

/** 購物清單空狀態提示。 */
export function ShoppingEmptyState() {
  return (
    <div className="shopping-empty card">
      <FiShoppingCart aria-hidden="true" />
      <h3>目前還沒有購物項目</h3>
      <p>新增第一筆購物項目開始管理採買清單</p>
    </div>
  );
}
