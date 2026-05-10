"""Recipe recommendation LLM client 封裝。"""

from __future__ import annotations

from typing import Protocol

from ai_server.app.infra.settings import get_settings


class RecipeLlmClientProtocol(Protocol):
    """定義 recipe LLM client 介面。"""

    def generate_recipe_json(self, prompt: str) -> str:
        """呼叫 LLM 並回傳文字結果。"""


class OllamaRecipeLlmClient:
    """透過 LangChain ChatOllama 呼叫本機 Ollama。"""

    def __init__(self) -> None:
        """建立 Ollama client。"""
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_text_model

    def generate_recipe_json(self, prompt: str) -> str:
        """執行 Ollama 推論並回傳文字內容。"""
        from langchain_core.messages import HumanMessage
        from langchain_ollama import ChatOllama

        llm = ChatOllama(model=self.model, base_url=self.base_url, temperature=0.2)
        response = llm.invoke([HumanMessage(content=prompt)])

        content = response.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
            return "\n".join(text_parts)
        return str(content)

