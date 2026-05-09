import { FiShoppingCart } from "react-icons/fi";
import { EmptyState } from "../common/EmptyState";

/** 購物清單空狀態提示。 */
export function ShoppingEmptyState() {
  return (
    <EmptyState
      as="div"
      className="shopping-empty card"
      icon={FiShoppingCart}
      title="目前還沒有購物項目"
      description="新增第一筆購物項目開始管理採買清單"
    />
  );
}
