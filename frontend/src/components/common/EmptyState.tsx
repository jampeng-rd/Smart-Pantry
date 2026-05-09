import type { IconType } from "react-icons";

interface EmptyStateProps {
  icon: IconType;
  title: string;
  description: string;
  className?: string;
  as?: "div" | "section";
}

/** 共用空狀態提示區塊。 */
export function EmptyState({ icon: Icon, title, description, className, as = "div" }: EmptyStateProps) {
  const Tag = as;
  return (
    <Tag className={className}>
      <Icon aria-hidden="true" />
      <h3>{title}</h3>
      <p>{description}</p>
    </Tag>
  );
}
