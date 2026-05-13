"""Email provider 本地最小寄信測試工具。"""

from __future__ import annotations

import argparse
import logging

from backend.app.infra.email_client import EmailMessage
from backend.app.infra.email_client_factory import build_email_client
from backend.app.infra.settings import get_settings

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """使用現有 settings + factory 建立 client 並送一封測試信。"""
    parser = argparse.ArgumentParser(description="Email provider 最小寄信測試")
    parser.add_argument("--to", required=True, help="收件者 Email")
    parser.add_argument("--subject", default="Smart Pantry Email Provider Debug", help="測試信主旨")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = get_settings()
    client = build_email_client(settings)

    LOGGER.info(
        "email debug send start provider=%s production_provider=%s to_email=%s client_class=%s",
        settings.email_provider,
        settings.production_email_provider,
        args.to,
        client.__class__.__name__,
    )

    result = client.send_email(
        EmailMessage(
            to_email=args.to,
            subject=args.subject,
            content_text="這是 Smart Pantry 的 email provider debug 測試信。",
        )
    )
    LOGGER.info("email debug send result success=%s error_message=%s", result.success, result.error_message)


if __name__ == "__main__":
    main()
