"""Alembic baseline migration 測試。"""

from __future__ import annotations

from pathlib import Path


def test_alembic_files_exist() -> None:
    """驗證 Alembic 基礎檔案存在。"""
    project_root = Path(__file__).resolve().parents[2]
    assert (project_root / "alembic.ini").exists()
    assert (project_root / "migrations" / "env.py").exists()
    assert (project_root / "migrations" / "script.py.mako").exists()


def test_baseline_revision_file_exists() -> None:
    """驗證 baseline revision 檔案存在且 revision id 正確。"""
    project_root = Path(__file__).resolve().parents[2]
    baseline_file = project_root / "migrations" / "versions" / "20260514_1201_baseline_schema.py"
    assert baseline_file.exists()

    content = baseline_file.read_text(encoding="utf-8")
    assert 'revision = "20260514_1201"' in content
    assert "def upgrade() -> None:" in content
    assert "def downgrade() -> None:" in content
