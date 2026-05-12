"""中文文本正規化工具。"""

from __future__ import annotations

# 詞彙替換優先，避免先做單字替換造成語意偏移。
PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("少许", "少許"),
    ("姜片", "薑片"),
    ("锅中", "鍋中"),
    ("西兰花", "西蘭花"),
    ("芦笋", "蘆筍"),
    ("鸡蛋", "雞蛋"),
    ("黄瓜", "黃瓜"),
    ("胡萝卜", "胡蘿蔔"),
    ("土豆", "馬鈴薯"),
    ("马铃薯", "馬鈴薯"),
    ("萝卜", "蘿蔔"),
    ("芫荽", "香菜"),
    ("花椰菜", "花椰菜"),
)

CHAR_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("姜", "薑"),
    ("锅", "鍋"),
    ("芦", "蘆"),
    ("笋", "筍"),
    ("兰", "蘭"),
    ("腌", "醃"),
    ("头", "頭"),
    ("备", "備"),
    ("适", "適"),
    ("蛎", "蠣"),
    ("萝", "蘿"),
    ("卜", "蔔"),
)


def normalize_to_traditional(text: str) -> str:
    """將常見簡中與非台灣常用詞彙正規化為繁體中文。"""
    normalized = text.strip()
    for source, target in PHRASE_REPLACEMENTS:
        normalized = normalized.replace(source, target)
    for source, target in CHAR_REPLACEMENTS:
        normalized = normalized.replace(source, target)
    return normalized
