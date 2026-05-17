import psycopg
"""
查單一使用者資料的更完整資料
"""

DB_URL = "輸入你的 Render External Database URL"
USER_ID = 1

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        print("=== user ===")
        cur.execute("""
            SELECT id, email, display_name, is_admin, created_at
            FROM users
            WHERE id = %s
        """, (USER_ID,))
        print(cur.fetchone())

        print("\n=== user_preferences ===")
        cur.execute("""
            SELECT *
            FROM user_preferences
            WHERE user_id = %s
        """, (USER_ID,))
        for row in cur.fetchall():
            print(row)

        print("\n=== billing_memberships ===")
        cur.execute("""
            SELECT id, tier, membership_status, provider, billing_mode, started_at, ended_at
            FROM billing_memberships
            WHERE user_id = %s
            ORDER BY id DESC
        """, (USER_ID,))
        for row in cur.fetchall():
            print(row)

        print("\n=== billing_transactions ===")
        cur.execute("""
            SELECT id, external_trade_no, transaction_status, amount, paid_at, failed_at
            FROM billing_transactions
            WHERE user_id = %s
            ORDER BY id DESC
        """, (USER_ID,))
        for row in cur.fetchall():
            print(row)

        print("\n=== refresh_tokens ===")
        cur.execute("""
            SELECT id, revoked_at, expires_at, created_at
            FROM refresh_tokens
            WHERE user_id = %s
            ORDER BY id DESC
        """, (USER_ID,))
        for row in cur.fetchall():
            print(row)
