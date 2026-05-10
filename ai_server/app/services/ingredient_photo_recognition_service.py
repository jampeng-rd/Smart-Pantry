"""食材照片辨識服務：組 prompt、呼叫 Vision、解析輸出。"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from ai_server.app.clients.ingredient_vision_client import IngredientVisionClientProtocol, IngredientVisionTimeoutError

LOGGER = logging.getLogger(__name__)
INGREDIENT_PHOTO_TIMEOUT_MESSAGE = "食材照片辨識逾時，請改用較清楚、單一或少量食材的照片後再試。"


class IngredientPhotoRecognitionError(Exception):
    """食材照片辨識處理錯誤（提供可顯示給使用者的中文訊息）。"""


class IngredientPhotoRecognitionService:
    """封裝 ingredient photo recognition 核心流程。"""

    def __init__(self, vision_client: IngredientVisionClientProtocol):
        """建立服務實例。"""
        self.vision_client = vision_client

    def recognize(self, image_path: str) -> dict[str, Any]:
        """辨識圖片食材候選並驗證格式。"""
        if not image_path:
            raise IngredientPhotoRecognitionError("缺少圖片路徑，請重新上傳後再試。")

        path = Path(image_path)
        if not path.exists():
            raise IngredientPhotoRecognitionError("找不到要辨識的圖片，請重新上傳後再試。")

        prompt = self._build_prompt()
        try:
            raw_text = self.vision_client.recognize_ingredient_candidates(prompt=prompt, image_path=image_path)
            LOGGER.info("ingredient photo vision raw_text length=%s", len(raw_text))
        except IngredientVisionTimeoutError as exc:
            raise IngredientPhotoRecognitionError(INGREDIENT_PHOTO_TIMEOUT_MESSAGE) from exc
        except FileNotFoundError as exc:
            raise IngredientPhotoRecognitionError("找不到要辨識的圖片，請重新上傳後再試。") from exc
        except Exception as exc:
            raise IngredientPhotoRecognitionError("目前無法完成食材照片辨識，請稍後再試。") from exc

        payload = self._parse_json_payload_optional(raw_text)
        if payload is not None:
            LOGGER.info("ingredient photo vision parse json success")
            return self._validate_result(payload)

        names = self._parse_candidate_names_from_text(raw_text)
        return self._build_result_from_names(names)

    def _build_prompt(self) -> str:
        """建立給 Vision 模型的輕量 prompt。"""
        return (
            "請用繁體中文列出圖片中的食材名稱，只輸出食材名稱。"
            "若有多個食材，請以逗號分隔，不要解釋。"
        )

    def _parse_json_payload_optional(self, raw_text: str) -> dict[str, Any] | None:
        """嘗試解析 Vision 回傳文字為 JSON，失敗時回傳 None。"""
        trimmed = raw_text.strip()
        if not trimmed:
            raise IngredientPhotoRecognitionError("AI 回傳內容為空，請稍後再試。")

        trimmed = self._strip_code_fence(trimmed)

        try:
            payload = json.loads(trimmed)
        except json.JSONDecodeError:
            LOGGER.warning("ingredient photo vision parse json failed")
            return None

        if not isinstance(payload, dict):
            return None
        return payload

    def _strip_code_fence(self, text: str) -> str:
        """剝除 ```json code fence。"""
        if not text.startswith("```"):
            return text
        lines = text.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            return text
        stripped = "\n".join(lines[1:-1]).strip()
        if stripped.lower().startswith("json"):
            return stripped[4:].strip()
        return stripped

    def _validate_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        """驗證並清理回傳結果欄位。"""
        candidate_items = payload.get("candidate_items")
        if not isinstance(candidate_items, list):
            raise IngredientPhotoRecognitionError("AI 回傳缺少候選食材資料，請稍後再試。")

        normalized_items: list[dict[str, Any]] = []
        for item in candidate_items:
            if not isinstance(item, dict):
                raise IngredientPhotoRecognitionError("AI 回傳候選食材格式不正確，請稍後再試。")

            required_fields = [
                "name",
                "category",
                "quantity",
                "unit",
                "expiration_date",
                "storage_location",
                "note",
            ]
            if any(field not in item for field in required_fields):
                raise IngredientPhotoRecognitionError("AI 回傳候選食材缺少必要欄位，請稍後再試。")

            try:
                quantity = float(item["quantity"])
            except (TypeError, ValueError) as exc:
                raise IngredientPhotoRecognitionError("AI 回傳候選食材數量格式不正確，請稍後再試。") from exc

            normalized_items.append(
                {
                    "name": str(item["name"]).strip(),
                    "category": str(item["category"]).strip(),
                    "quantity": int(quantity) if quantity.is_integer() else quantity,
                    "unit": str(item["unit"]).strip(),
                    "expiration_date": item["expiration_date"],
                    "storage_location": str(item["storage_location"]).strip(),
                    "note": str(item["note"]).strip() or "AI 辨識候選，請確認",
                }
            )

        if not normalized_items:
            raise IngredientPhotoRecognitionError("AI 未辨識出可用食材，請換一張照片再試。")

        note = payload.get("note")
        if not isinstance(note, str) or not note.strip():
            note = "AI 食材照片辨識結果，請使用者確認後再加入庫存。"

        return {
            "candidate_items": normalized_items,
            "note": note,
        }

    def _parse_candidate_names_from_text(self, raw_text: str) -> list[str]:
        """從自然語言回覆解析食材名稱。"""
        cleaned = raw_text.strip()
        cleaned = self._strip_code_fence(cleaned)
        cleaned = cleaned.replace("，", ",").replace("、", ",").replace("。", ",")
        cleaned = re.sub(r"圖片中有|照片中有|看起來有|有一顆|有一個|有", "", cleaned)

        tokens = [part.strip() for part in cleaned.split(",") if part.strip()]
        names: list[str] = []
        for token in tokens:
            normalized = self._normalize_zh_variant(token)
            normalized = re.sub(r"^(一顆|一個|一份)", "", normalized).strip()
            if normalized and re.search(r"[A-Za-z0-9\u4e00-\u9fff]", normalized):
                names.append(normalized)

        deduped: list[str] = []
        seen: set[str] = set()
        for name in names:
            if name not in seen:
                seen.add(name)
                deduped.append(name)
        if not deduped:
            raise IngredientPhotoRecognitionError("AI 回傳格式無法解析，請稍後再試。")
        return deduped

    def _normalize_zh_variant(self, text: str) -> str:
        """最小化常見簡體字轉換。"""
        mapping = {
            "西红柿": "西紅柿",
            "鸡蛋": "雞蛋",
            "马铃薯": "馬鈴薯",
            "萝卜": "蘿蔔",
            "黄瓜": "黃瓜",
            "茄子": "茄子",
            "蘑菇": "蘑菇",
        }
        normalized = text.strip()
        for simplified, traditional in mapping.items():
            normalized = normalized.replace(simplified, traditional)
        return normalized

    def _build_result_from_names(self, names: list[str]) -> dict[str, Any]:
        """依名稱清單建立標準 candidate_items 結構。"""
        candidate_items = [
            {
                "name": name,
                "category": "未分類",
                "quantity": 1,
                "unit": "份",
                "expiration_date": None,
                "storage_location": "fridge",
                "note": "AI 辨識候選，請確認",
            }
            for name in names
        ]
        return {
            "candidate_items": candidate_items,
            "note": "AI 食材照片辨識結果，請使用者確認後再加入庫存。",
        }
