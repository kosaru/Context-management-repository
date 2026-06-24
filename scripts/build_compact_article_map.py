#!/usr/bin/env python3
"""Build compact navigation maps without creating empty article cards."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import collect_note as base
import note_index

MAP_DIR = base.ROOT / "articles" / "maps"
MASTER = base.ROOT / "articles" / "COMPACT_MAP.md"

GROUPS = {
    "phase_01": ("第1期：2026-01-24〜02-10", "PHASE_01.md", "analysis/PHASE_01_2026-01-24_TO_02-10.md"),
    "phase_02": ("第2期：2026-02-11〜02-27", "PHASE_02.md", "analysis/PHASE_02_2026-02-11_TO_02-27.md"),
    "phase_03": ("第3期：2026-03-02〜03-13", "PHASE_03.md", "analysis/PHASE_03_2026-03-02_TO_03-13.md"),
    "phase_04": ("第4期：2026-03-14〜03-21", "PHASE_04.md", "analysis/PHASE_04_2026-03-14_TO_03-21.md"),
    "phase_05": ("第5期：2026-03-24〜03-31", "PHASE_05.md", "analysis/PHASE_05_2026-03-24_TO_03-31.md"),
    "phase_06": ("第6期：2026-03-23／04-01〜05-01", "PHASE_06.md", "analysis/PHASE_06_2026-03-23_TO_05-01.md"),
    "individual": ("後期個別記事：2026-05-05〜06-23", "INDIVIDUAL_2026-05_TO_06.md", "articles/CROSS_ROLES.md"),
}
ORDER = list(GROUPS)

KEYWORDS = {
    "A": r"人類|文明|持続|環境|気候|人口|資源|エネルギー|減速|生命|未来",
    "B": r"政治|制度|責任|民主|投票|右翼|左翼|中道|保存|再設計|回転|国会|リベラル",
    "C": r"安心|不安|効率|ゆとり|労働|価格|景気|都市|家庭|ケア|移動|生活|所得|税|雇用",
    "D": r"倫理|共同体|アドラー|主体|教育|道場|家族|救済|関係|世代|文化|思想",
    "E": r"科学|メディア|資料|検証|抽象|単線|複雑|情報|気象|文献|報道|事実|原因|構造",
    "F": r"AI|ChatGPT|NotebookLM|Claude|Gemini|プロンプト|Repair|生成AI|モデル|文脈",
}


def esc(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def opening(snapshot: str, limit: int = 140) -> str:
    path = base.ROOT / snapshot
    if not snapshot or not path.exists():
        return "本文スナップショット未取得。"
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        marker = text.find("\n---\n", 4)
        if marker >= 0:
            text = text[marker + 5 :]
    paragraphs = []
    buf = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if buf:
                paragraphs.append(" ".join(buf)); buf = []
            continue
        if line.startswith("#") or "公開本文の正本" in line or "取得時スナップショット" in line:
            continue
        line = re.sub(r"^>\s*|^[-*+]\s+|^\d+[.)]\s+", "", line)
        line = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", line)
        line = re.sub(r"[`*_~]", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            buf.append(line)
    if buf:
        paragraphs.append(" ".join(buf))
    candidates = [p for p in paragraphs if len(p) >= 20 and not p.startswith(("※", "関連研究", "研究名", "研究者", "本文との"))]
    if candidates and "生成AIとの対話を通じて" in candidates[0][:100]:
        candidates = candidates[1:]
    joined = " ".join(candidates[:3]) or "冒頭要旨を自動抽出できなかった。"
    if len(joined) <= limit:
        return joined
    part = joined[: limit + 20]
    pos = max(part.rfind("。", 70), part.rfind("？", 70), part.rfind("！", 70))
    return part[: pos + 1] if pos >= 70 else joined[:limit].rstrip("、。") + "…"


def role(title: str) -> str:
    if re.search(r"改訂|修正|訂正|補足|追記|再考", title): return "修正・補記"
    if re.search(r"まとめ|整理|振り返|全体像|現在地", title): return "自己整理・統合"
    if re.search(r"メモ|雑記|試論|仮説", title): return "試行メモ"
    if re.search(r"第[0-9一二三四五六七八九十]+回|第[一二三四五六七八九十]+弾|連載", title): return "連載・展開"
    if re.search(r"なぜ|とは|どう|何が|どこで|誰が|[?？]", title): return "問い・考察"
    return "考察"


def lineage(title: str, summary: str) -> str:
    text = title + " " + summary
    found = [code for code, pattern in KEYWORDS.items() if re.search(pattern, text, re.I)]
    return "・".join((found or ["E"])[:3])


def group(record: dict) -> str:
    unit = str(record.get("analysis_unit") or "")
    if unit in GROUPS:
        return unit
    return "individual"


def rows() -> list[dict[str, str]]:
    catalog = note_index.load_articles(note_index.CATALOG_PATH)
    coverage = note_index.load_articles(note_index.COVERAGE_PATH)
    cards = note_index.grouped_cards()
    result = []
    for note_id, current in catalog.items():
        covered = coverage.get(note_id, {})
        card_items = cards.get(note_id, [])
        card = note_index.choose_canonical(card_items) if card_items else None
        summary = opening(str(current.get("snapshot_path") or ""))
        result.append({
            "id": note_id,
            "date": str(current.get("published_at") or ""),
            "title": str(current.get("title") or note_id),
            "url": str(current.get("note_url") or ""),
            "summary": summary,
            "role": role(str(current.get("title") or "")),
            "lineage": lineage(str(current.get("title") or ""), summary),
            "group": group(covered),
            "analysis_ref": str(covered.get("analysis_ref") or ""),
            "card": str((card or {}).get("relative_path") or ""),
        })
    result.sort(key=lambda item: (item["date"], item["id"]))
    for i, item in enumerate(result):
        item["previous"] = result[i - 1]["id"] if i else ""
        item["next"] = result[i + 1]["id"] if i + 1 < len(result) else ""
    return result


def reference(item: dict[str, str]) -> str:
    if item["card"]:
        return f"[個別カード](../{item['card']})"
    label, _, default_ref = GROUPS[item["group"]]
    ref = item["analysis_ref"] or default_ref
    return f"[{label}](../../{ref})"


def neighbor(note_id: str, arrow: str) -> str:
    return f"[{arrow}{note_id}](https://note.com/shirokuma1970/n/{note_id})" if note_id else "—"


def write_group(name: str, data: list[dict[str, str]]) -> None:
    label, filename, _ = GROUPS[name]
    subset = [item for item in data if item["group"] == name]
    lines = [
        f"# コンパクト記事地図――{label}", "",
        "ナビゲーション用の索引。冒頭要旨・役割候補・系譜候補は暫定であり、詳細解析ではない。", "",
        "系譜：A 人類継続・文明保存・減速／B 保存・再設計・回転・責任配置／C Security・Comfort・内部条件／D 倫理・主体・共同体／E 検証・抽象化・情報／F AI・読解・Repair", "",
        f"記事数：{len(subset)}件", "",
        "| 公開日 | note ID | 記事 | 冒頭要旨（暫定） | 役割候補 | 系譜候補 | 前後 | 詳細参照 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in subset:
        title = f"[{esc(item['title'])}]({item['url']})" if item["url"] else esc(item["title"])
        before = neighbor(item["previous"], "←")
        after = neighbor(item["next"], "") + "→" if item["next"] else "—"
        lines.append(f"| {item['date']} | `{item['id']}` | {title} | {esc(item['summary'])} | {item['role']} | {item['lineage']} | {before}<br>{after} | {reference(item)} |")
    (MAP_DIR / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_master(data: list[dict[str, str]]) -> None:
    counts = Counter(item["group"] for item in data)
    cards = sum(bool(item["card"]) for item in data)
    lines = [
        "# 全351記事コンパクト地図", "",
        "空の個別カードを大量に置かず、全記事の所在・冒頭要旨・接続候補を記事単位で追うための索引。", "",
        "- 冒頭要旨は本文冒頭からの自動抽出であり、中心命題の確定ではない。",
        "- 役割候補と系譜候補は暫定分類であり、個別カード・時期別解析より優先しない。",
        "- 詳細な判断が必要な記事だけ個別カードへ昇格する。", "",
        f"- 全記事：{len(data)}件",
        f"- 個別カードあり：{cards}件",
        f"- コンパクト地図のみ：{len(data) - cards}件", "",
        "| 区分 | 記事数 | 地図 | 詳細解析 |", "|---|---:|---|---|",
    ]
    for name in ORDER:
        label, filename, ref = GROUPS[name]
        lines.append(f"| {label} | {counts.get(name, 0)} | [{filename}](maps/{filename}) | [{Path(ref).name}](../{ref}) |")
    lines += ["", "個別カードへ昇格する対象：概念・問いの初出、既存系譜を変える修正・反例、複数系譜の統合稿、事実と推論の厳密な分離が必要な記事。"]
    MASTER.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    data = rows()
    for name in ORDER:
        write_group(name, data)
    write_master(data)
    print(f"compact map: {len(data)} articles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
