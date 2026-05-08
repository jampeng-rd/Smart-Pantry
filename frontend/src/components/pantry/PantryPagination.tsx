import { Pagination } from "../common/Pagination";

interface PantryPaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
}

/** Pantry 分頁控制列（包裝共用 Pagination）。 */
export function PantryPagination(props: PantryPaginationProps) {
  return <Pagination {...props} pageSizeOptions={[10, 20, 50]} />;
}
