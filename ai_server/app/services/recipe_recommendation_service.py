"""食譜推薦服務：組 prompt、呼叫 LLM、解析輸出。"""

from __future__ import annotations

import json
import re
from typing import Any

from ai_server.app.clients.recipe_llm_client import RecipeLlmClientProtocol
from ai_server.app.utils.zh_text import normalize_to_traditional


class RecipeRecommendationError(Exception):
    """食譜推薦處理錯誤（提供可顯示給使用者的中文訊息）。"""


class RecipeRecommendationService:
    """封裝 recipe recommendation 的核心流程。"""

    REQUIRED_FIELDS = {
        "recipe_name": str,
        "ingredients_used": list,
        "missing_ingredients": list,
        "steps": list,
        "cooking_time_minutes": int,
        "note": str,
    }

    def __init__(self, llm_client: RecipeLlmClientProtocol):
        """建立服務實例。"""
        self.llm_client = llm_client

    def recommend(self, input_snapshot: dict[str, Any], pantry_items: list[dict[str, Any]]) -> dict[str, Any]:
        """產生食譜推薦結果並驗證格式。"""
        prompt = self._build_prompt(input_snapshot=input_snapshot, pantry_items=pantry_items)
        raw_text = self.llm_client.generate_recipe_json(prompt)
        payload = self._parse_json_payload(raw_text)
        return self._validate_result(payload)

    def _build_prompt(self, input_snapshot: dict[str, Any], pantry_items: list[dict[str, Any]]) -> str:
        """建立給 LLM 的 JSON-only prompt。"""
        request_payload = {
            "cooking_time_minutes": input_snapshot.get("cooking_time_minutes"),
            "cooking_tools": input_snapshot.get("cooking_tools") or [],
            "diet_preference": input_snapshot.get("diet_preference"),
            "allergies": input_snapshot.get("allergies") or [],
            "prioritize_expiring_soon": bool(input_snapshot.get("prioritize_expiring_soon", False)),
            "pantry_items": pantry_items,
        }

        return (
            "你是智慧食材系統的食譜推薦助手。"
            "請僅輸出單一 JSON 物件，不要輸出 markdown、前後說明或其他文字。\n"
            "所有輸出必須使用繁體中文，不可使用簡體中文。\n"
            "JSON 必須包含欄位：recipe_name、ingredients_used、missing_ingredients、steps、cooking_time_minutes、note。\n"
            "- ingredients_used/missing_ingredients/steps 必須是陣列\n"
            "- cooking_time_minutes 必須是整數\n"
            "- note 請加上『僅供生活參考』提醒\n"
            f"輸入資料：{json.dumps(request_payload, ensure_ascii=False)}"
        )

    def _parse_json_payload(self, raw_text: str) -> dict[str, Any]:
        """解析 LLM 回傳文字為 JSON。"""
        trimmed = raw_text.strip()
        if not trimmed:
            raise RecipeRecommendationError("AI 回傳內容為空，請稍後再試。")

        # 支援 ```json ... ``` 包裝
        if trimmed.startswith("```"):
            lines = trimmed.splitlines()
            if len(lines) >= 3 and lines[-1].strip() == "```":
                trimmed = "\n".join(lines[1:-1]).strip()
                if trimmed.lower().startswith("json"):
                    trimmed = trimmed[4:].strip()

        try:
            payload = json.loads(trimmed)
        except json.JSONDecodeError as exc:
            raise RecipeRecommendationError("AI 回傳格式無法解析，請稍後再試。") from exc

        if not isinstance(payload, dict):
            raise RecipeRecommendationError("AI 回傳格式不正確，請稍後再試。")
        return payload

    def _validate_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        """驗證並清理回傳結果欄位。"""
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in payload:
                raise RecipeRecommendationError("AI 回傳缺少必要欄位，請稍後再試。")
            if not isinstance(payload[field], field_type):
                raise RecipeRecommendationError("AI 回傳欄位格式不正確，請稍後再試。")

        sanitized_recipe_name = self._sanitize_recipe_name(payload["recipe_name"])
        if not sanitized_recipe_name:
            raise RecipeRecommendationError("AI 回傳食譜名稱為空，請稍後再試。")
        if not payload["steps"]:
            raise RecipeRecommendationError("AI 回傳步驟為空，請稍後再試。")
        if payload["cooking_time_minutes"] <= 0:
            raise RecipeRecommendationError("AI 回傳烹調時間不正確，請稍後再試。")

        # 強制輸出相容格式
        return {
            "recipe_name": sanitized_recipe_name,
            "ingredients_used": [self._sanitize_ingredient_text(str(item)) for item in payload["ingredients_used"]],
            "missing_ingredients": [self._sanitize_ingredient_text(str(item)) for item in payload["missing_ingredients"]],
            "steps": [normalize_to_traditional(str(step)) for step in payload["steps"]],
            "cooking_time_minutes": int(payload["cooking_time_minutes"]),
            "note": normalize_to_traditional(payload["note"]),
        }

    def _sanitize_recipe_name(self, name: str) -> str:
        """清理食譜名稱前後異常 o/O 雜訊字元。"""
        normalized = normalize_to_traditional(str(name)).strip()
        without_prefix = re.sub(r"^[oO]+", "", normalized)
        without_edges = re.sub(r"[oO]+$", "", without_prefix)
        return without_edges.strip()

    def _sanitize_ingredient_text(self, text: str) -> str:
        """清理食材文字中的整數浮點表示（例如 10.0 -> 10）。"""
        normalized = normalize_to_traditional(text)
        return re.sub(r"(?<!\d)(\d+)\.0(?!\d)", r"\1", normalized)
