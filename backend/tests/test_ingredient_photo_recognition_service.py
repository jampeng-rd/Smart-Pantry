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

    assert str(exc.value) == "食材照片辨識逾時，請稍後再試。"


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
