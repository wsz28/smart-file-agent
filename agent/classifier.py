"""
classifier.py
三级分类策略，逐级兜底，不依赖单一手段：
  第 1 级：文本内容关键词识别（票据 / 合同等，读文本头部）
  第 2 级：扩展名规则（rules.json）
  第 3 级：可选大模型裁决（缺省 / 未配置时跳过）
"""
import json
import os
from pathlib import Path

from . import llm


def load_rules(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _sniff_text(path: Path, limit: int = 1024) -> str:
    """尝试读取文件开头文本，用于关键词匹配。失败则返回空串。"""
    try:
        if path.suffix.lower() in (".pdf",):
            return _sniff_pdf(path, limit)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""


def _sniff_pdf(path: Path, limit: int) -> str:
    """极简 PDF 文本嗅探：从二进制里抓可见 ASCII 片段。"""
    try:
        data = path.read_bytes()[: limit * 4]
        # 取可打印字符块
        return " ".join(ch for ch in data if 32 <= ch < 127)[:limit]
    except Exception:
        return ""


def _keyword_hit(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def classify_by_keywords(path: Path, categories) -> str:
    """第 1 级：文本关键词。返回分类名，未命中返回 None。"""
    text = _sniff_text(path)
    if not text:
        return None
    for cat in categories:
        if cat.get("keywords") and _keyword_hit(text, cat["keywords"]):
            return cat["name"]
    return None


def classify_by_ext(path: Path, categories, default: str) -> str:
    """第 2 级：扩展名规则。"""
    ext = path.suffix.lower()
    for cat in categories:
        if ext in cat.get("extensions", []):
            return cat["name"]
    return default


def classify_file(path: Path, categories, default: str, use_llm: bool = False):
    """
    三级分类：关键词 -> 扩展名 -> 大模型（可选）。
    返回 (分类名, 命中级别)。level: keyword / extension / llm / default
    """
    # 1) 文本关键词
    kw = classify_by_keywords(path, categories)
    if kw:
        return kw, "keyword"

    # 2) 扩展名
    ext_cat = classify_by_ext(path, categories, default)
    if ext_cat != default:
        return ext_cat, "extension"

    # 3) 可选大模型
    if use_llm and llm.enabled():
        try:
            name = llm.ask_classify(path)
            if name:
                return name, "llm"
        except Exception:
            pass

    return default, "default"
