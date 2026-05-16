export type BillingMode = "one_time" | "subscription";

export interface BillingMembershipSummary {
  is_pro: boolean;
  tier: string;
  membership_status: string;
  provider: string | null;
  billing_mode: BillingMode | null;
  started_at: string | null;
  ended_at: string | null;
}

export interface BillingUpgradeEntryData {
  billing_mode: BillingMode;
  upgrade_entry_path: string;
  one_time_entry_path: string;
  subscription_entry_path: string;
  membership: BillingMembershipSummary;
  message: string;
}

export interface BillingOneTimeCheckoutData {
  transaction_id: number;
  external_trade_no: string;
  gateway_url: string;
  merchant_id: string;
  trade_info: string;
  trade_sha: string;
  version: string;
}

export interface BillingTransactionStatusData {
  external_trade_no: string;
  transaction_status: string;
  membership_status: string;
  is_pro: boolean;
  amount: number;
  paid_at: string | null;
  failed_at: string | null;
}
