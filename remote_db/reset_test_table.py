import psycopg
"""
清空所有資料表
"""

DB_URL = "你的 Render External Database URL"

tables = [
    "refresh_tokens",
    "password_reset_tokens",
    "expiration_reminder_deliveries",
    "billing_webhook_events",
    "billing_transactions",
    "billing_memberships",
    "pantry_items",
    "shopping_list_items",
    "user_preferences",
]

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        for table in tables:
            sql = f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"
            print(f"running: {sql}")
            cur.execute(sql)
    conn.commit()

print("測試資料已清空")
