import psycopg
"""
清空單一資料表
"""

DB_URL = "輸入你的 Render External Database URL"
TABLE_NAME = "refresh_tokens"

allowed_tables = {
    "refresh_tokens",
    "users",
    "pantry_items",
    "shopping_list_items",
    "user_preferences",
    "password_reset_tokens",
    "expiration_reminder_deliveries",
    "billing_transactions",
    "billing_memberships",
    "billing_webhook_events",
}

if TABLE_NAME not in allowed_tables:
    raise ValueError(f"不允許操作的資料表: {TABLE_NAME}")

sql = f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY CASCADE;"

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

print(f"{TABLE_NAME} 已清空")
