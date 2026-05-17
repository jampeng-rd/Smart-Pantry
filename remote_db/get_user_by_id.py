import psycopg
"""
檢查單一使用者資料 (用 id 查)
"""

DB_URL = "輸入你的 Render External Database URL"
USER_ID = 1

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, email, display_name, is_admin, created_at
            FROM users
            WHERE id = %s
        """, (USER_ID,))
        row = cur.fetchone()

print(row)
