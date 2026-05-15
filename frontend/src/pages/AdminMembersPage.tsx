import { useEffect, useMemo, useState } from "react";
import { FiShield } from "react-icons/fi";

import { ErrorState } from "../components/common/ErrorState";
import { LoadingState } from "../components/common/LoadingState";
import { Pagination } from "../components/common/Pagination";
import type { AdminMemberItem } from "../features/admin/adminTypes";
import { adminApi } from "../services/apiClient";
import { formatLocalDateTime } from "../utils/dateTime";

const DEFAULT_PAGE_SIZE = 10;

/** Admin 會員管理頁。 */
export function AdminMembersPage() {
  const [items, setItems] = useState<AdminMemberItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let alive = true;

    const loadMembers = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await adminApi.listMembers({ page, pageSize });
        if (!alive) {
          return;
        }
        setItems(data.items);
        setTotal(data.total);
      } catch (err) {
        if (!alive) {
          return;
        }
        setError(err instanceof Error ? err.message : "載入會員列表失敗");
      } finally {
        if (alive) {
          setLoading(false);
        }
      }
    };

    void loadMembers();

    return () => {
      alive = false;
    };
  }, [page, pageSize, retryKey]);

  const hasData = items.length > 0;
  const emptyMessage = useMemo(() => (loading ? "" : "目前沒有可顯示的會員資料。"), [loading]);

  return (
    <section className="card workspace-card">
      <h2 className="workspace-title">
        <FiShield aria-hidden="true" /> 會員管理
      </h2>
      <p className="workspace-phase">Admin 基礎會員列表</p>

      {loading ? <LoadingState text="載入會員資料中..." className="workspace-loading" /> : null}
      {error ? (
        <ErrorState
          message={error}
          className="workspace-error"
          actionsClassName="workspace-error-actions"
          onRetry={() => setRetryKey((prev) => prev + 1)}
          onClose={() => setError(null)}
        />
      ) : null}

      {!loading && !error && !hasData ? <p>{emptyMessage}</p> : null}

      {!loading && !error && hasData ? (
        <div className="table-like-wrapper">
          <table className="table-like">
            <thead>
              <tr>
                <th>會員 ID</th>
                <th>Email</th>
                <th>顯示名稱</th>
                <th>角色</th>
                <th>建立時間</th>
              </tr>
            </thead>
            <tbody>
              {items.map((member) => (
                <tr key={member.id}>
                  <td>{member.id}</td>
                  <td>{member.email}</td>
                  <td>{member.display_name}</td>
                  <td>{member.is_admin ? "管理員" : "一般會員"}</td>
                  <td>{formatLocalDateTime(member.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {!loading && !error && hasData ? (
        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={setPage}
          onPageSizeChange={(nextSize) => {
            setPageSize(nextSize);
            setPage(1);
          }}
          pageSizeOptions={[10, 20, 50]}
        />
      ) : null}
    </section>
  );
}
