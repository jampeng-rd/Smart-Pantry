import { useEffect, useMemo, useRef, useState } from "react";
import { FiChevronDown, FiChevronUp, FiSearch, FiShield } from "react-icons/fi";

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
  const [searchKeyword, setSearchKeyword] = useState("");
  const [expandedMemberIds, setExpandedMemberIds] = useState<number[]>([]);
  const latestRequestIdRef = useRef(0);

  useEffect(() => {
    let alive = true;

    const loadMembers = async () => {
      const currentRequestId = latestRequestIdRef.current + 1;
      latestRequestIdRef.current = currentRequestId;
      setLoading(true);
      setError(null);
      try {
        const data = await adminApi.listMembers({ page, pageSize, q: searchKeyword });
        if (!alive || currentRequestId !== latestRequestIdRef.current) {
          return;
        }
        setItems(data.items);
        setTotal(data.total);
      } catch (err) {
        if (!alive || currentRequestId !== latestRequestIdRef.current) {
          return;
        }
        setError(err instanceof Error ? err.message : "載入會員列表失敗");
      } finally {
        if (alive && currentRequestId === latestRequestIdRef.current) {
          setLoading(false);
        }
      }
    };

    void loadMembers();

    return () => {
      alive = false;
    };
  }, [page, pageSize, retryKey, searchKeyword]);

  const hasData = items.length > 0;
  const emptyMessage = useMemo(() => {
    if (loading) {
      return "";
    }
    if (searchKeyword.trim()) {
      return "找不到符合條件的會員。";
    }
    return "目前沒有可顯示的會員資料。";
  }, [loading, searchKeyword]);

  return (
    <section className="card workspace-card admin-members-page">
      <h2 className="workspace-title">
        <FiShield aria-hidden="true" /> 會員管理
      </h2>
      <p className="workspace-phase">依會員 ID 由小到大顯示，可搜尋名稱與 Email</p>

      <div className="admin-members-toolbar">
        <label className="admin-members-search" htmlFor="admin-members-search-input">
          <FiSearch aria-hidden="true" />
          <input
            id="admin-members-search-input"
            type="search"
            value={searchKeyword}
            placeholder="搜尋名字或 Email"
            onChange={(event) => {
              setSearchKeyword(event.target.value);
              setPage(1);
              setExpandedMemberIds([]);
            }}
          />
        </label>
      </div>

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
        <div className="admin-members-list">
          {items.map((member) => (
            <article
              key={member.id}
              className={`admin-member-row${expandedMemberIds.includes(member.id) ? " expanded" : ""}`}
              aria-label={`會員 ${member.display_name}`}
            >
              <div className="admin-member-field admin-member-desktop-field">
                <p className="admin-member-label">會員 ID</p>
                <p className="admin-member-value">#{member.id}</p>
              </div>
              <div className="admin-member-field admin-member-desktop-field">
                <p className="admin-member-label">顯示名稱</p>
                <p className="admin-member-value">{member.display_name}</p>
              </div>
              <div className="admin-member-field admin-member-desktop-field admin-member-field-email">
                <p className="admin-member-label">Email</p>
                <p className="admin-member-value">{member.email}</p>
              </div>
              <div className="admin-member-field admin-member-desktop-field">
                <p className="admin-member-label">角色</p>
                <p className={`admin-member-role ${member.is_admin ? "admin" : "member"}`}>{member.is_admin ? "管理員" : "一般會員"}</p>
              </div>
              <div className="admin-member-field admin-member-desktop-field">
                <p className="admin-member-label">建立時間</p>
                <p className="admin-member-value">{formatLocalDateTime(member.created_at)}</p>
              </div>
              <div className="admin-member-field admin-member-mobile-summary admin-member-field-email">
                <p className="admin-member-label">Email</p>
                <p className="admin-member-value">{member.email}</p>
              </div>
              <div className="admin-member-field admin-member-mobile-summary">
                <p className="admin-member-label">顯示名稱</p>
                <p className="admin-member-value">{member.display_name}</p>
              </div>
              <div className="admin-member-field admin-member-detail-field">
                <p className="admin-member-label">會員 ID</p>
                <p className="admin-member-value">#{member.id}</p>
              </div>
              <div className="admin-member-field admin-member-detail-field">
                <p className="admin-member-label">角色</p>
                <p className={`admin-member-role ${member.is_admin ? "admin" : "member"}`}>{member.is_admin ? "管理員" : "一般會員"}</p>
              </div>
              <div className="admin-member-field admin-member-detail-field">
                <p className="admin-member-label">建立時間</p>
                <p className="admin-member-value">{formatLocalDateTime(member.created_at)}</p>
              </div>
              <button
                type="button"
                className="btn ghost admin-member-expand-btn"
                onClick={() =>
                  setExpandedMemberIds((prev) =>
                    prev.includes(member.id) ? prev.filter((id) => id !== member.id) : [...prev, member.id],
                  )
                }
                aria-label={expandedMemberIds.includes(member.id) ? "收合詳細資料" : "展開詳細資料"}
              >
                {expandedMemberIds.includes(member.id) ? <FiChevronUp aria-hidden="true" /> : <FiChevronDown aria-hidden="true" />}
                {expandedMemberIds.includes(member.id) ? "收合詳細資料" : "展開詳細資料"}
              </button>
            </article>
          ))}
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
