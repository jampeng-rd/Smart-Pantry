import type { ReactNode } from "react";

interface StatusBadgeProps {
  label: string;
  tone: "normal" | "soon" | "expired";
  icon?: ReactNode;
}

/** 共用狀態標籤。 */
export function StatusBadge({ label, tone, icon }: StatusBadgeProps) {
  const toneClassName = tone === "normal" ? "pantry-status-normal" : tone === "soon" ? "pantry-status-soon" : "pantry-status-expired";
  return (
    <span className={`pantry-status ${toneClassName}`}>
      {icon}
      {label}
    </span>
  );
}
