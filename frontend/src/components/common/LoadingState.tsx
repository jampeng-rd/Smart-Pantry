interface LoadingStateProps {
  text: string;
  className: string;
}

/** 共用載入中提示區塊。 */
export function LoadingState({ text, className }: LoadingStateProps) {
  return <div className={className}>{text}</div>;
}
