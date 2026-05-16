import { useState } from "react";
import { FiAlertCircle, FiCheckCircle, FiCreditCard, FiLoader, FiSend } from "react-icons/fi";

import { billingApi } from "../services/apiClient";

/** 藍新單次付款入口頁。 */
export function BillingNewebpayOneTimePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 向後端建立交易並導向藍新付款頁。 */
  const handleCheckout = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await billingApi.createNewebPayOneTimeCheckout();
      const form = document.createElement("form");
      form.method = "POST";
      form.action = data.gateway_url;
      form.style.display = "none";

      const fields: Record<string, string> = {
        MerchantID: data.merchant_id,
        TradeInfo: data.trade_info,
        TradeSha: data.trade_sha,
        Version: data.version,
      };
      Object.entries(fields).forEach(([name, value]) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = name;
        input.value = value;
        form.appendChild(input);
      });
      document.body.appendChild(form);
      form.submit();
    } catch (apiError) {
      const message = apiError instanceof Error ? apiError.message : "";
      setError(message.includes("網路異常") ? "網路異常，請稍後再試。" : message || "建立付款交易失敗，請稍後再試。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card workspace-card billing-one-time-page">
      <h2 className="workspace-title">
        <FiCreditCard aria-hidden="true" /> 藍新單次付款
      </h2>
      <div className="billing-upgrade-summary">
        <p>
          <strong>方案：</strong>PRO 單次升級
        </p>
        <p>
          <strong>金額：</strong>NT$99（一次付清）
        </p>
        <p>
          <strong>付款方式：</strong>信用卡一次付清
        </p>
      </div>
      <button type="button" className="btn primary" aria-label="前往藍新測試付款頁" disabled={loading} onClick={() => void handleCheckout()}>
        {loading ? <FiLoader aria-hidden="true" /> : <FiSend aria-hidden="true" />} {loading ? "建立交易中..." : "前往藍新付款"}
      </button>
      {error ? (
        <p className="error-text">
          <FiAlertCircle aria-hidden="true" /> {error}
        </p>
      ) : (
        <p className="muted-text">
          <FiCheckCircle aria-hidden="true" /> 送出後將跳轉到藍新測試付款頁。
        </p>
      )}
    </section>
  );
}
