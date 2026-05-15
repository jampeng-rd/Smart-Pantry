"""初始化第一個 admin 帳號的命令列工具。"""

from __future__ import annotations

import argparse

from fastapi import HTTPException

from backend.app.infra.database import SessionLocal
from backend.app.infra.repository.admin_member_repository import AdminMemberRepository
from backend.app.services.admin_member_service import AdminMemberService


DEFAULT_ADMIN_EMAIL = "jampeng.rd@gmail.com"


def build_parser() -> argparse.ArgumentParser:
    """建立 bootstrap admin CLI 參數解析器。"""
    parser = argparse.ArgumentParser(description="建立或更新第一個 admin 帳號")
    parser.add_argument("--email", default=DEFAULT_ADMIN_EMAIL, help="要設為 admin 的 email")
    parser.add_argument("--create-if-not-exists", action="store_true", help="若使用者不存在則建立新帳號")
    parser.add_argument("--password", default=None, help="建立新帳號時使用的密碼")
    parser.add_argument("--display-name", default="系統管理員", help="建立新帳號時的顯示名稱")
    return parser


def run_bootstrap_admin(
    email: str,
    create_if_not_exists: bool,
    password: str | None,
    display_name: str | None,
) -> tuple[str, bool]:
    """執行 admin bootstrap 邏輯。"""
    db = SessionLocal()
    try:
        repository = AdminMemberRepository(db=db)
        service = AdminMemberService(repository=repository)
        return service.bootstrap_admin(
            email=email,
            create_if_not_exists=create_if_not_exists,
            password=password,
            display_name=display_name,
        )
    finally:
        db.close()


def main() -> int:
    """命令列進入點。"""
    parser = build_parser()
    args = parser.parse_args()

    try:
        message, _ = run_bootstrap_admin(
            email=args.email,
            create_if_not_exists=args.create_if_not_exists,
            password=args.password,
            display_name=args.display_name,
        )
    except HTTPException as exc:
        print(f"[失敗] {exc.detail}")
        return 1

    print(f"[完成] {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
