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


def test_recipe_prompt_should_require_traditional_chinese() -> None:
    """prompt 應要求輸出繁體中文。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"番茄炒蛋","ingredients_used":["番茄","雞蛋"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":10,"note":"僅供生活參考"}'
        )
    )

    prompt = service._build_prompt(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert "所有輸出必須使用繁體中文，不可使用簡體中文" in prompt


def test_recommend_should_normalize_simplified_chinese_phrases() -> None:
    """食譜結果應套用繁中正規化。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"家常炒蛋","ingredients_used":["鸡蛋"],"missing_ingredients":["姜片"],"steps":["撒上少许鹽和姜片"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])

    assert result["ingredients_used"] == ["雞蛋"]
    assert result["missing_ingredients"] == ["薑片"]
    assert result["steps"] == ["撒上少許鹽和薑片"]


def test_recipe_name_should_sanitize_prefix_o() -> None:
    """食譜名稱應清理前綴 o/O 雜訊。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"ooooo秋刀魚煎蛋","ingredients_used":["秋刀魚","雞蛋"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["recipe_name"] == "秋刀魚煎蛋"


def test_recipe_name_should_sanitize_suffix_o() -> None:
    """食譜名稱應清理後綴 o/O 雜訊。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"秋刀魚煎蛋oooo","ingredients_used":["秋刀魚","雞蛋"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["recipe_name"] == "秋刀魚煎蛋"


def test_recipe_name_should_sanitize_prefix_and_suffix_o() -> None:
    """食譜名稱應清理前後綴 o/O 雜訊。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"ooooo秋刀魚煎蛋oooo","ingredients_used":["秋刀魚","雞蛋"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["recipe_name"] == "秋刀魚煎蛋"


def test_recipe_name_should_keep_normal_name() -> None:
    """正常食譜名稱不應被影響。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"家常番茄炒蛋","ingredients_used":["番茄","雞蛋"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["recipe_name"] == "家常番茄炒蛋"


def test_ingredient_text_should_remove_integer_decimal_suffix() -> None:
    """食材文字中的整數浮點應清理為整數。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"家常番茄炒蛋","ingredients_used":["雞蛋 15.0 顆"],"missing_ingredients":["三文魚 1.0 份"],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["ingredients_used"] == ["雞蛋 15 顆"]
    assert result["missing_ingredients"] == ["三文魚 1 份"]


def test_ingredient_text_should_keep_real_decimal() -> None:
    """真實小數應保留，不可被轉為整數。"""
    service = RecipeRecommendationService(
        llm_client=FakeRecipeLlmClient(
            '{"recipe_name":"家常番茄炒蛋","ingredients_used":["牛奶 1.5 杯"],"missing_ingredients":[],"steps":["步驟"],"cooking_time_minutes":8,"note":"僅供生活參考"}'
        )
    )

    result = service.recommend(input_snapshot={}, pantry_items=[{"name": "雞蛋", "status": "normal"}])
    assert result["ingredients_used"] == ["牛奶 1.5 杯"]
