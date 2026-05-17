import { useEffect, useState } from "react";
import { FiArrowRight, FiCheckCircle, FiRefreshCw } from "react-icons/fi";

import { formatMembershipStatusZh } from "../features/billing/billingFormatters";
import type { BillingUpgradeEntryData } from "../features/billing/billingTypes";
import { billingApi } from "../services/apiClient";

interface BillingUpgradePageProps {
  onNavigate: (path: string) => void;
}

/** Billing 升級統一入口頁。 */
export function BillingUpgradePage({ onNavigate }: BillingUpgradePageProps) {
  const [data, setData] = useState<BillingUpgradeEntryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await billingApi.getUpgradeEntry();
      setData(response);
    } catch (apiError) {
      const message = apiError instanceof Error ? apiError.message : "";
      setError(message.includes("網路異常") ? "網路異常，請稍後再試。" : "目前系統偵測異常，系統維修中。");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (loading) {
    return <section className="card workspace-card">載入升級方案中...</section>;
  }

  if (error || !data) {
    return (
      <section className="card workspace-card billing-upgrade-page">
        <p>{error ?? "目前無法取得升級資訊"}</p>
        <button type="button" className="btn ghost" aria-label="重試載入升級資訊" onClick={() => void load()}>
          <FiRefreshCw aria-hidden="true" /> 重新整理
        </button>
      </section>
    );
  }

  const targetPath = data.upgrade_entry_path;
  const targetLabel = data.billing_mode === "one_time" ? "前往單次付款頁" : "前往訂閱付款頁";

  return (
    <section className="card workspace-card billing-upgrade-page">
      <p className="muted-text">{data.message}</p>
      <div className="billing-upgrade-summary">
        <p>
          <strong>目前方案：</strong>
          {data.membership.tier}
        </p>
        <p>
          <strong>會員狀態：</strong>
          {formatMembershipStatusZh(data.membership.membership_status)}
        </p>
        <p>
          <strong>是否為 PRO：</strong>
          {data.membership.is_pro ? "是" : "否"}
        </p>
        {data.membership.is_pro && data.membership.membership_status === "active" ? (
          <p className="muted-text">
            <FiCheckCircle aria-hidden="true" /> 已升級為 PRO（狀態：啟用）
          </p>
        ) : null}
      </div>
      <div className="billing-upgrade-actions">
        <button type="button" className="btn primary" aria-label={targetLabel} onClick={() => onNavigate(targetPath)}>
          <FiArrowRight aria-hidden="true" /> {targetLabel}
        </button>
      </div>
      <p className="muted-text">
        <FiCheckCircle aria-hidden="true" /> 升級流程已支援藍新單次付款測試環境。
      </p>
    </section>
  );
}
