import psycopg
"""
刪除單一使用者
"""

DB_URL = "輸入你的 Render External Database URL"
USER_ID = 2

with psycopg.connect(DB_URL, connect_timeout=10) as conn:
    with conn.cursor() as cur:
        # 先查這個使用者
        cur.execute("SELECT id, email, display_name, is_admin FROM users WHERE id = %s", (USER_ID,))
        user = cur.fetchone()
        print("user =", user)

        if not user:
            print("找不到該使用者，結束")
            raise SystemExit(0)

        # 依你目前系統可能有的關聯資料，先刪子表
        cur.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM pantry_items WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM shopping_list_items WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM user_preferences WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM expiration_reminder_deliveries WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM billing_webhook_events WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM billing_transactions WHERE user_id = %s", (USER_ID,))
        cur.execute("DELETE FROM billing_memberships WHERE user_id = %s", (USER_ID,))

        # 最後再刪 users
        cur.execute("DELETE FROM users WHERE id = %s", (USER_ID,))

    conn.commit()

print("刪除完成")
