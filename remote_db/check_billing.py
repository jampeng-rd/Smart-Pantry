import psycopg
"""
檢查全部付款狀態
"""

DB_URL = "輸入你的 Render External Database URL"

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, user_id, external_trade_no, transaction_status, amount, paid_at, failed_at, membership_id
            FROM billing_transactions
            ORDER BY id DESC
            LIMIT 10
        """)
        print("=== billing_transactions ===")
        for row in cur.fetchall():
            print(row)

        cur.execute("""
            SELECT id, user_id, tier, membership_status, provider, billing_mode, started_at, ended_at
            FROM billing_memberships
            ORDER BY id DESC
            LIMIT 10
        """)
        print("\n=== billing_memberships ===")
        for row in cur.fetchall():
            print(row)

        cur.execute("""
            SELECT id, user_id, event_type, provider_event_id, processing_status, error_message, received_at, processed_at
            FROM billing_webhook_events
            ORDER BY id DESC
            LIMIT 10
        """)
        print("\n=== billing_webhook_events ===")
        for row in cur.fetchall():
            print(row)
