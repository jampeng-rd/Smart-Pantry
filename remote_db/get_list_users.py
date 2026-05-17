import psycopg
"""
檢查全部使用者資料
"""

DB_URL = "輸入你的 Render External Database URL"

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, email, display_name, is_admin, created_at
            FROM users
            ORDER BY id ASC
        """)
        rows = cur.fetchall()

for row in rows:
    print(row)
