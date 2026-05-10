"""Phase 08-2 食譜推薦服務測試（不呼叫真實 Ollama）。"""

from __future__ import annotations

import pytest

from ai_server.app.services.recipe_recommendation_service import RecipeRecommendationError, RecipeRecommendationService


class FakeRecipeLlmClient:
    """測試用假 LLM client。"""

    def __init__(self, response_text: str):
        """設定回傳字串。"""
        self.response_text = response_text

    def generate_recipe_json(self, prompt: str) -> str:
        """回傳固定字串。"""
        _ = prompt
        return self.response_text


def test_recommend_success_with_valid_json() -> None:
    """合法 JSON 可產生相容格式結果。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"番茄炒蛋","ingredients_used":["番茄","雞蛋"],"missing_ingredients":["鹽"],"steps":["備料","拌炒"],"cooking_time_minutes":12,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["recipe_name"] == "番茄炒蛋"
    assert set(result.keys()) == {
        "recipe_name",
        "ingredients_used",
        "missing_ingredients",
        "steps",
        "cooking_time_minutes",
        "note",
    }


def test_recommend_fail_when_json_missing_required_field() -> None:
    """缺欄位時應拋出中文錯誤。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient('{"recipe_name":"炒蛋","ingredients_used":[],"missing_ingredients":[],"steps":[],"note":"僅供生活參考"}')
    )

    with pytest.raises(RecipeRecommendationError) as exc:
        service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])

    assert "缺少必要欄位" in str(exc.value)


def test_recommend_fail_when_not_json() -> None:
    """非 JSON 回傳應拋出中文錯誤。"""
    service = RecipeRecommendationService(llm_client=FakeRecipeLlmClient("not json"))

    with pytest.raises(RecipeRecommendationError) as exc:
        service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])

    assert "無法解析" in str(exc.value)

