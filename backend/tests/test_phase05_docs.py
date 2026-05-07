"""Phase 05 文件規範測試。"""

from pathlib import Path


def test_phase05_docs_should_record_utc_and_shopping_flow() -> None:
    """文件需記錄 UTC、時區顯示策略與購物完成流程。"""
    project_root = Path(__file__).resolve().parents[2]
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    phase_doc = (project_root / "docs" / "phase-05-shopping-list.md").read_text(encoding="utf-8")

    assert "UTC" in readme
    assert "timezone" in readme
    assert "瀏覽器" in readme
    assert "不會自動更新 pantry" in readme

    assert "UTC" in phase_doc
    assert "瀏覽器時區" in phase_doc
    assert "is_purchased=true" in phase_doc
    assert "不自動更新 pantry" in phase_doc
    assert "convert-to-pantry" in phase_doc
