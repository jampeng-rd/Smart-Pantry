import psycopg
"""
更新單一使用者資料 (改 EMAIL)
"""

DB_URL = "你的新的 Render External Database URL"
USER_ID = 2
NEW_EMAIL = "newmail@example.com"

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users
            SET email = %s
            WHERE id = %s
            RETURNING id, email, display_name, is_admin
        """, (NEW_EMAIL, USER_ID))
        updated = cur.fetchone()
    conn.commit()

print("updated =", updated)
