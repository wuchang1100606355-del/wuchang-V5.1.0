"""
五常社區知識庫：壓縮上下文 + 索引生成器

輸入：wuchang_community_knowledge_base.json
輸出：
  - wuchang_community_context_compact.md
  - wuchang_community_knowledge_index.json

設計目標：
  - 給 AI 用的短上下文（可直接貼進 prompt）
  - 給系統用的可機器檢索索引（path/snippet/keywords + inverted index）
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Tuple


DEFAULT_KB = "wuchang_community_knowledge_base.json"
DEFAULT_OUT_INDEX = "wuchang_community_knowledge_index.json"
DEFAULT_OUT_CONTEXT = "wuchang_community_context_compact.md"


def _tokenize(text: str) -> List[str]:
    s = (text or "").strip().lower()
    if not s:
        return []
    tokens: List[str] = []
    tokens.extend([t for t in re.split(r"[^a-z0-9_]+", s) if len(t) >= 2])
    # Chinese segments
    for seg in re.findall(r"[\u4e00-\u9fff]{2,12}", text):
        tokens.append(seg)
        # 2~4 char ngrams for better recall
        for n in (2, 3, 4):
            if len(seg) >= n:
                for i in range(0, len(seg) - n + 1):
                    tokens.append(seg[i:i+n])
    # Dedup preserve order
    seen = set()
    out = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _shorten(value: Any, max_len: int = 220) -> str:
    s = str(value)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _walk(obj: Any, path: str = "", items: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    if items is None:
        items = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            # Index leaf-ish nodes
            if isinstance(v, (str, int, float, bool)) or v is None:
                items.append(
                    {
                        "path": p,
                        "title": k,
                        "snippet": _shorten(v),
                    }
                )
            elif isinstance(v, list) and all(isinstance(x, (str, int, float, bool)) or x is None for x in v):
                items.append(
                    {
                        "path": p,
                        "title": k,
                        "snippet": _shorten(v),
                    }
                )
            else:
                _walk(v, p, items)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}[{i}]"
            if isinstance(v, (str, int, float, bool)) or v is None:
                items.append({"path": p, "title": path.split(".")[-1] if path else "item", "snippet": _shorten(v)})
            else:
                _walk(v, p, items)

    return items


def build_index(kb: Dict[str, Any]) -> Dict[str, Any]:
    raw_items = _walk(kb)

    items: List[Dict[str, Any]] = []
    inverted_index: Dict[str, List[str]] = {}
    section_stats: Dict[str, Counter] = {}

    def section_of(path: str) -> str:
        # first segment of path, e.g. demographics.xxx => demographics
        if not path:
            return "root"
        if path.startswith("["):
            return "root"
        return path.split(".", 1)[0].split("[", 1)[0]

    for i, it in enumerate(raw_items, 1):
        sid = section_of(it["path"])
        text_for_kw = f"{it.get('title','')} {it.get('snippet','')} {it.get('path','')}"
        kws = _tokenize(text_for_kw)
        # keep keywords small & focused
        keywords = kws[:12]
        item_id = f"kb_{i:05d}"
        out = {
            "id": item_id,
            "section": sid,
            "path": it["path"],
            "title": it.get("title", ""),
            "snippet": it.get("snippet", ""),
            "keywords": keywords,
        }
        items.append(out)

        if sid not in section_stats:
            section_stats[sid] = Counter()
        section_stats[sid].update(keywords)

        for kw in keywords:
            inverted_index.setdefault(kw, []).append(item_id)

    section_summaries = {}
    for sid, ctr in section_stats.items():
        section_summaries[sid] = {
            "top_keywords": [k for k, _ in ctr.most_common(12)],
            "items": sum(ctr.values()),
        }

    return {
        "index_version": "1.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": DEFAULT_KB,
        "community_name": kb.get("community_name") or kb.get("community") or "N/A",
        "items_count": len(items),
        "section_summaries": section_summaries,
        "items": items,
        "inverted_index": inverted_index,
    }


def build_compact_context(kb: Dict[str, Any]) -> str:
    # Compose a compact, AI-friendly context block from high-signal fields.
    parts: List[str] = []
    parts.append("# 五常社區：壓縮上下文（給 AI 小 J）")
    parts.append("")
    parts.append(f"- 更新日期: {kb.get('last_updated', 'N/A')}")
    parts.append(f"- 範圍: {', '.join((kb.get('scope', {}).get('villages') or []))}")
    parts.append(f"- 社區名稱: {kb.get('community_name', 'N/A')}")

    key_stats = kb.get("key_statistics", {})
    if key_stats:
        parts.append("")
        parts.append("## 關鍵統計")
        for k, v in key_stats.items():
            parts.append(f"- {k}: {v}")

    insights = kb.get("critical_insights", [])
    if insights:
        parts.append("")
        parts.append("## 關鍵洞察（必記）")
        for it in insights[:12]:
            parts.append(f"- {_shorten(it, 240)}")

    # Pull a few high-value operational recommendations
    rec = kb.get("strategic_recommendations", {})
    if rec:
        parts.append("")
        parts.append("## 策略建議（系統設計對接）")
        # Keep stable order
        for k in ["ui_ux", "logistics", "b2b", "happiness_coin", "rollout_strategy"]:
            if k in rec:
                parts.append(f"- {k}: {_shorten(rec[k], 300)}")

    # Add a minimal “why this matters” anchor for the God view concept
    parts.append("")
    parts.append("## 上帝視角（Little J 知道、我就要知道）")
    parts.append("- 任何決策/建議需附：引用路徑(path) + 依據片段(snippet) + 風險/假設。")
    parts.append("- 回答要能回溯到知識庫索引項目（便於稽核與追責）。")

    parts.append("")
    parts.append("## 使用方式（給系統）")
    parts.append("- 先查索引：/api/community/knowledge/search?q=...")
    parts.append("- 再用 path 回到知識庫取原文（必要時）。")

    parts.append("")
    return "\n".join(parts)


def main():
    kb_path = os.getenv("KB_PATH", DEFAULT_KB)
    out_index = os.getenv("OUT_INDEX", DEFAULT_OUT_INDEX)
    out_context = os.getenv("OUT_CONTEXT", DEFAULT_OUT_CONTEXT)

    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    index = build_index(kb)
    context = build_compact_context(kb)

    with open(out_index, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    with open(out_context, "w", encoding="utf-8") as f:
        f.write(context)

    print(f"[OK] wrote: {out_index} ({len(json.dumps(index, ensure_ascii=False))} chars)")
    print(f"[OK] wrote: {out_context} ({len(context)} chars)")


if __name__ == "__main__":
    main()

