import type { ReactNode } from "react";
import { FiAlertCircle } from "react-icons/fi";

interface ErrorStateProps {
  message: string;
  className: string;
  actionsClassName: string;
  onRetry?: () => void;
  onClose: () => void;
  retryText?: string;
  retryIcon?: ReactNode;
}

/** 共用錯誤提示區塊。 */
export function ErrorState({ message, className, actionsClassName, onRetry, onClose, retryText = "重試", retryIcon }: ErrorStateProps) {
  return (
    <div className={className} role="alert">
      <p>
        <FiAlertCircle aria-hidden="true" /> {message}
      </p>
      <div className={actionsClassName}>
        {onRetry ? (
          <button type="button" className="btn ghost" onClick={onRetry}>
            {retryIcon}
            {retryText}
          </button>
        ) : null}
        <button type="button" className="btn ghost" onClick={onClose}>
          關閉
        </button>
      </div>
    </div>
  );
}
