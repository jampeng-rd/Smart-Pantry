"""AI job DB polling worker 骨架。"""

from __future__ import annotations

import logging
import time

from ai_server.app.infra.settings import get_settings

LOGGER = logging.getLogger(__name__)


def poll_once() -> None:
    """執行一次 polling 週期（Phase 08-0 骨架）。"""
    settings = get_settings()
    LOGGER.info(
        "poll once: batch_size=%s timeout=%s",
        settings.ai_worker_batch_size,
        settings.ai_job_timeout_seconds,
    )
    # Phase 08-1 開始補上：
    # 1. 從 ai_jobs 撈取 pending
    # 2. claim 為 running
    # 3. 呼叫 fake handler
    # 4. 寫回 success/failed


def run_forever() -> None:
    """持續執行 DB polling worker。"""
    settings = get_settings()
    LOGGER.info("ai worker started, poll_interval=%s", settings.ai_worker_poll_interval_seconds)
    while True:
        poll_once()
        time.sleep(settings.ai_worker_poll_interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_forever()
