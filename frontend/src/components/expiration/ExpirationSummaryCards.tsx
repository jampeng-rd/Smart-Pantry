import { FiAlertTriangle, FiCheckCircle, FiClock, FiLayers } from "react-icons/fi";

import type { ExpirationSummaryStats } from "../../features/expiration/expirationTypes";

interface ExpirationSummaryCardsProps {
  stats: ExpirationSummaryStats;
}

/** 到期提醒摘要卡片區塊。 */
export function ExpirationSummaryCards({ stats }: ExpirationSummaryCardsProps) {
  return (
    <section className="expiration-summary-grid" aria-label="到期提醒摘要">
      <article className="card expiration-summary-card is-expired">
        <p className="expiration-summary-label">
          <FiAlertTriangle aria-hidden="true" /> 已過期
        </p>
        <p className="expiration-summary-value">{stats.expired}</p>
      </article>

      <article className="card expiration-summary-card is-soon">
        <p className="expiration-summary-label">
          <FiClock aria-hidden="true" /> 即將到期
        </p>
        <p className="expiration-summary-value">{stats.expiringSoon}</p>
      </article>

      <article className="card expiration-summary-card is-normal">
        <p className="expiration-summary-label">
          <FiCheckCircle aria-hidden="true" /> 正常
        </p>
        <p className="expiration-summary-value">{stats.normal}</p>
      </article>

      <article className="card expiration-summary-card is-total">
        <p className="expiration-summary-label">
          <FiLayers aria-hidden="true" /> 全部
        </p>
        <p className="expiration-summary-value">{stats.total}</p>
      </article>
    </section>
  );
}
