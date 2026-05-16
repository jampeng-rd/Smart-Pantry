import { useEffect, useMemo, useState } from "react";
import { FiAlertCircle, FiCheckCircle, FiClock, FiCreditCard, FiXCircle } from "react-icons/fi";

import type { BillingTransactionStatusData } from "../features/billing/billingTypes";
import { billingApi } from "../services/apiClient";

/** 藍新單次付款結果頁。 */
export function BillingNewebpayOneTimeResultPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusData, setStatusData] = useState<BillingTransactionStatusData | null>(null);
  const externalTradeNo = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("external_trade_no") ?? "";
  }, []);

  useEffect(() => {
    if (!externalTradeNo) {
      setError("缺少交易編號，請回到升級頁面重新操作。");
      setLoading(false);
      return;
    }
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await billingApi.getNewebPayOneTimeTransactionStatus(externalTradeNo);
        setStatusData(data);
      } catch (apiError) {
        const message = apiError instanceof Error ? apiError.message : "";
        setError(message.includes("網路異常") ? "網路異常，請稍後再試。" : message || "查詢交易結果失敗。");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [externalTradeNo]);

  const statusLabel = useMemo(() => {
    if (!statusData) {
      return null;
    }
    if (statusData.transaction_status === "success") {
      return { text: "付款成功，已啟用 PRO", icon: <FiCheckCircle aria-hidden="true" /> };
    }
    if (statusData.transaction_status === "failed") {
      return { text: "付款失敗，尚未升級", icon: <FiXCircle aria-hidden="true" /> };
    }
    return { text: "交易處理中，請稍後再重新整理", icon: <FiClock aria-hidden="true" /> };
  }, [statusData]);

  return (
    <section className="card workspace-card billing-one-time-page">
      <h2 className="workspace-title">
        <FiCreditCard aria-hidden="true" /> 單次付款結果
      </h2>
      {loading ? <p>載入交易狀態中...</p> : null}
      {error ? (
        <p className="error-text">
          <FiAlertCircle aria-hidden="true" /> {error}
        </p>
      ) : null}
      {!loading && !error && statusData && statusLabel ? (
        <>
          <div className="billing-upgrade-summary">
            <p>
              <strong>交易編號：</strong>
              {statusData.external_trade_no}
            </p>
            <p>
              <strong>交易狀態：</strong>
              {statusData.transaction_status}
            </p>
            <p>
              <strong>會員狀態：</strong>
              {statusData.membership_status}
            </p>
            <p>
              <strong>目前方案：</strong>
              {statusData.is_pro ? "PRO" : "FREE"}
            </p>
          </div>
          <p className={statusData.transaction_status === "success" ? "muted-text" : "error-text"}>
            {statusLabel.icon} {statusLabel.text}
          </p>
        </>
      ) : null}
    </section>
  );
}
