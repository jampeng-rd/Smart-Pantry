"""Ingredient photo Vision client 封裝。"""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Protocol

from ai_server.app.infra.settings import get_settings

LOGGER = logging.getLogger(__name__)


class IngredientVisionTimeoutError(Exception):
    """Vision 模型呼叫逾時錯誤。"""


class IngredientVisionClientProtocol(Protocol):
    """定義 ingredient vision client 介面。"""

    def recognize_ingredient_candidates(self, prompt: str, image_path: str) -> str:
        """呼叫 Vision 模型並回傳文字結果。"""


class OllamaIngredientVisionClient:
    """透過 Ollama Python client 呼叫本機 Vision 模型。"""

    def __init__(self) -> None:
        """建立 Ollama Vision client。"""
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_vision_model
        self.timeout_seconds = settings.ai_vision_timeout_seconds

    def recognize_ingredient_candidates(self, prompt: str, image_path: str) -> str:
        """執行 Vision 推論並回傳 message.content。"""
        import ollama
        from httpx import TimeoutException

        path = Path(image_path)
        image_base64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        client = ollama.Client(host=self.base_url, timeout=self.timeout_seconds)
        try:
            response = client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_base64],
                    }
                ],
                stream=False,
                options={"temperature": 0.2},
            )
        except TimeoutError as exc:
            raise IngredientVisionTimeoutError("vision timeout") from exc
        except TimeoutException as exc:
            raise IngredientVisionTimeoutError("vision timeout") from exc

        message = getattr(response, "message", None)
        content = getattr(message, "content", "")
        content_text = content if isinstance(content, str) else ""
        LOGGER.info(
            "ingredient vision response summary type=%s model=%s done=%s content_length=%s",
            type(response).__name__,
            getattr(response, "model", None),
            getattr(response, "done", None),
            len(content_text),
        )
        return content_text
