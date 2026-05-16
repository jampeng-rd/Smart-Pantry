"""Billing 設定驗證測試。"""

from __future__ import annotations

import pytest

from backend.app.infra.settings import Settings


def test_settings_should_accept_billing_mode_one_time() -> None:
    """BILLING_MODE=one_time 應可通過。"""
    settings = Settings(billing_mode="one_time")
    assert settings.billing_mode == "one_time"


def test_settings_should_accept_billing_mode_subscription() -> None:
    """BILLING_MODE=subscription 應可通過。"""
    settings = Settings(billing_mode="subscription")
    assert settings.billing_mode == "subscription"


def test_settings_should_reject_unknown_billing_mode() -> None:
    """BILLING_MODE 非法值應拒絕。"""
    with pytest.raises(ValueError) as exc:
        Settings(billing_mode="invalid_mode")

    assert "BILLING_MODE" in str(exc.value)
