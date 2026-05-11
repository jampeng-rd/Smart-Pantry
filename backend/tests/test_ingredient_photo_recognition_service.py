"""Ingredient photo recognition service 測試。"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_server.app.clients.ingredient_vision_client import IngredientVisionTimeoutError
from ai_server.app.services.ingredient_photo_recognition_service import IngredientPhotoRecognitionError, IngredientPhotoRecognitionService


class FakeVisionClient:
    """測試用假 Vision client。"""

    def __init__(self, response_text: str):
        self.response_text = response_text

    def recognize_ingredient_candidates(self, prompt: str, image_path: str) -> str:
        _ = prompt
        _ = image_path
        return self.response_text


class FakeTimeoutVisionClient:
    """測試用逾時 Vision client。"""

    def recognize_ingredient_candidates(self, prompt: str, image_path: str) -> str:
        _ = prompt
        _ = image_path
        raise IngredientVisionTimeoutError("timeout")


class FakeThinkingOnlyVisionClient:
    """測試用僅有 thinking、content 為空的 Vision client。"""

    def recognize_ingredient_candidates(self, prompt: str, image_path: str) -> str:
        _ = prompt
        _ = image_path
        return ""


def test_recognition_success_parses_candidate_items(tmp_path: Path) -> None:
    """可成功解析 candidate_items。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(
        vision_client=FakeVisionClient(
            '{"candidate_items":[{"name":"番茄","category":"蔬菜","quantity":1,"unit":"顆","expiration_date":null,"storage_location":"fridge","note":"AI 辨識候選，請確認"}],"note":"AI 食材照片辨識結果，請使用者確認後再加入庫存。"}'
        )
    )

    result = service.recognize(str(image_path))

    assert "candidate_items" in result
    assert len(result["candidate_items"]) == 1
    assert result["candidate_items"][0]["name"] == "番茄"


def test_recognition_plain_text_single_name_should_success(tmp_path: Path) -> None:
    """Vision 回傳單一名稱文字時應成功。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient("番茄"))

    result = service.recognize(str(image_path))
    assert len(result["candidate_items"]) == 1
    assert result["candidate_items"][0]["name"] == "番茄"
    assert result["candidate_items"][0]["category"] == "未分類"


def test_recognition_plain_text_multi_names_should_success(tmp_path: Path) -> None:
    """Vision 回傳多名稱文字時應成功。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient("番茄、雞蛋"))

    result = service.recognize(str(image_path))
    assert len(result["candidate_items"]) == 2
    assert result["candidate_items"][0]["name"] == "番茄"
    assert result["candidate_items"][1]["name"] == "雞蛋"


def test_recognition_sentence_text_should_success(tmp_path: Path) -> None:
    """Vision 回傳句型文字時應可解析出名稱。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient("圖片中有一顆番茄。"))

    result = service.recognize(str(image_path))
    assert len(result["candidate_items"]) == 1
    assert result["candidate_items"][0]["name"] == "番茄"


def test_recognition_image_not_found_should_fail() -> None:
    """圖片不存在時應失敗。"""
    service = IngredientPhotoRecognitionService(
        vision_client=FakeVisionClient(
            '{"candidate_items":[{"name":"番茄","category":"蔬菜","quantity":1,"unit":"顆","expiration_date":null,"storage_location":"fridge","note":"AI 辨識候選，請確認"}],"note":"AI 食材照片辨識結果，請使用者確認後再加入庫存。"}'
        )
    )

    with pytest.raises(IngredientPhotoRecognitionError) as exc:
        service.recognize("uploads/ingredient_photos/not-exists.jpg")

    assert "找不到要辨識的圖片" in str(exc.value)


def test_recognition_timeout_should_fail_with_friendly_message(tmp_path: Path) -> None:
    """Vision 逾時時應回傳中文友善訊息。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeTimeoutVisionClient())

    with pytest.raises(IngredientPhotoRecognitionError) as exc:
        service.recognize(str(image_path))

    assert str(exc.value) == "食材照片辨識逾時，請改用較清楚、單一或少量食材的照片後再試。"


def test_recognition_empty_content_should_fail(tmp_path: Path) -> None:
    """Vision 回傳空字串時應失敗。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient(""))

    with pytest.raises(IngredientPhotoRecognitionError) as exc:
        service.recognize(str(image_path))

    assert "AI 回傳內容為空" in str(exc.value)


def test_recognition_json_payload_should_still_success(tmp_path: Path) -> None:
    """若模型回合法 JSON，仍應走 JSON parser 成功。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(
        vision_client=FakeVisionClient(
            '{"candidate_items":[{"name":"番茄","category":"蔬菜","quantity":1,"unit":"顆","expiration_date":null,"storage_location":"fridge","note":"AI 辨識候選，請確認"}],"note":"AI 食材照片辨識結果，請使用者確認後再加入庫存。"}'
        )
    )

    result = service.recognize(str(image_path))
    assert len(result["candidate_items"]) == 1
    assert result["candidate_items"][0]["name"] == "番茄"


def test_recognition_thinking_only_without_content_should_fail(tmp_path: Path) -> None:
    """若僅有 thinking 但 content 為空，不應視為成功。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeThinkingOnlyVisionClient())

    with pytest.raises(IngredientPhotoRecognitionError) as exc:
        service.recognize(str(image_path))

    assert "AI 回傳內容為空" in str(exc.value)


def test_build_prompt_should_include_multi_ingredient_and_output_constraints() -> None:
    """prompt 應強調多食材辨識與輕量輸出限制。"""
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient("番茄"))
    prompt = service._build_prompt()

    assert "盡量列出所有清楚可見的食材名稱" in prompt
    assert "多個食材請用逗號分隔" in prompt
    assert "所有輸出必須使用繁體中文，不可使用簡體中文" in prompt
    assert "不要輸出料理名稱、餐具、包裝品牌、說明文字或 markdown" in prompt


def test_recognition_plain_text_should_apply_extended_zh_variant_mapping(tmp_path: Path) -> None:
    """常見簡體字詞應轉為繁體。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(vision_client=FakeVisionClient("芦笋、西兰花、芫荽"))

    result = service.recognize(str(image_path))
    names = [item["name"] for item in result["candidate_items"]]

    assert "蘆筍" in names
    assert "西蘭花" in names
    assert "香菜" in names


def test_recognition_json_payload_should_apply_normalize_to_candidate_fields(tmp_path: Path) -> None:
    """JSON payload 欄位應套用繁中正規化。"""
    image_path = tmp_path / "ingredient.jpg"
    image_path.write_bytes(b"fake-image")
    service = IngredientPhotoRecognitionService(
        vision_client=FakeVisionClient(
            '{"candidate_items":[{"name":"芫荽","category":"锅中蔬菜","quantity":1,"unit":"份","expiration_date":null,"storage_location":"fridge","note":"少许姜片"}],"note":"加入芫荽"}'
        )
    )

    result = service.recognize(str(image_path))
    item = result["candidate_items"][0]

    assert item["name"] == "香菜"
    assert item["category"] == "鍋中蔬菜"
    assert item["unit"] == "份"
    assert item["note"] == "少許薑片"
    assert result["note"] == "加入香菜"
