"""zh_text 正規化工具測試。"""

from ai_server.app.utils.zh_text import normalize_to_traditional


def test_normalize_to_traditional_should_apply_phrase_first() -> None:
    """詞彙替換應優先於單字替換。"""
    text = "撒上少许鹽和姜片，再放入锅中拌炒。"

    normalized = normalize_to_traditional(text)

    assert normalized == "撒上少許鹽和薑片，再放入鍋中拌炒。"


def test_normalize_to_traditional_should_apply_taiwan_common_terms() -> None:
    """常見台灣用語應正規化。"""
    text = "芦笋、西兰花、芫荽、土豆、黄瓜、胡萝卜"

    normalized = normalize_to_traditional(text)

    assert normalized == "蘆筍、西蘭花、香菜、馬鈴薯、黃瓜、胡蘿蔔"
