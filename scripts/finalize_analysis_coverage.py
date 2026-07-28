#!/usr/bin/env python3
"""Protect the initial analyzed corpus from automatic future assignment.

The first run records the current coverage note IDs as the baseline corpus.
On later runs, entries outside that baseline that were automatically marked
covered in the same run are reset to pending. This prevents a newly discovered,
backdated article from being absorbed into an old phase merely because its
published date falls inside that phase range.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import collect_note as base

COVERAGE_PATH = base.ROOT / "analysis" / "COVERAGE.json"
BASELINE_PATH = base.ROOT / "analysis" / "BASELINE_NOTE_IDS.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def replace(path: str, old: str, new: str) -> None:
    target = base.ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"missing expected text in {path}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def finalize_n494_once() -> None:
    """Apply the explicit review decision only inside the one-time Actions run."""
    if os.getenv("GITHUB_ACTIONS") != "true":
        return

    target_id = "n4940d2f00d0a"
    card_path = base.ROOT / "articles" / "cards" / "2026-07-06-n4940d2f00d0a.md"
    if not card_path.exists() or not COVERAGE_PATH.exists():
        return

    coverage = load_json(COVERAGE_PATH)
    entry = coverage.get("articles", {}).get(target_id, {})
    if isinstance(entry, dict) and entry.get("analysis_state") == "covered" and entry.get("role"):
        return

    subprocess.run(
        [
            "python",
            "scripts/update_analysis_coverage.py",
            "--accept",
            target_id,
            "--coverage-type",
            "individual_card",
            "--analysis-ref",
            "articles/cards/2026-07-06-n4940d2f00d0a.md",
            "--role",
            "皇統の判定原理・民意の前提・旧宮家案",
        ],
        cwd=base.ROOT,
        check=True,
    )

    replace("START_HERE.md", "新規・原文先行カード4件を作成した", "新規・原文先行カード5件を作成した")
    replace("START_HERE.md", "文脈解析あり：357件", "文脈解析あり：358件")
    replace("START_HERE.md", "個別カードあり：104件（詳細カード79件＋未解析カード25件）", "個別カードあり：104件（詳細カード80件＋未解析カード24件）")
    replace("START_HERE.md", "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
    replace(
        "START_HERE.md",
        "13. `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n14. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n15. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n16. `analysis/stabilization_audit/OPERATIONS.md`",
        "13. `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n14. `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`\n15. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n16. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n17. `analysis/stabilization_audit/OPERATIONS.md`",
    )

    progress = "analysis/INDIVIDUAL_ARTICLE_REVIEW_PROGRESS.md"
    replace(progress, "詳細カード：79件", "詳細カード：80件")
    replace(progress, "`PENDING`：4件（新規・原文先行）", "`PENDING`：5件（新規・原文先行）")
    replace(progress, "未解析カード：25件", "未解析カード：24件")
    replace(progress, "## 詳細カード79件の割当て", "## 詳細カード80件の割当て")
    replace(
        progress,
        "| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md` |\n| 合計 | 79 |",
        "| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md` |\n| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md` |\n| 合計 | 80 |",
    )

    key = "analysis/KEY_ARTICLE_SELECTION.md"
    replace(key, "詳細カード：79件", "詳細カード：80件")
    replace(key, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
    replace(key, "詳細カード79件は、次の監査台帳へ記録した。", "詳細カード80件は、次の監査台帳へ記録した。")
    replace(key, "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`", "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n- `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`")

    register = "analysis/STABILIZATION_AUDIT_REGISTER.md"
    replace(register, "新規・原文先行カード4件を管理する", "新規・原文先行カード5件を管理する")
    replace(register, "新規・原文先行分析・ユーザー確認待ち：4件", "新規・原文先行分析・ユーザー確認待ち：5件")
    replace(register, "## 個別カード79件の現在地", "## 個別カード80件の現在地")
    replace(register, "`PENDING`：4件", "`PENDING`：5件")
    replace(register, "4件は新規・原文先行分析のユーザー確認待ち", "5件は新規・原文先行分析のユーザー確認待ち")
    replace(register, "## 新規・原文先行分析4件", "## 新規・原文先行分析5件")
    replace(
        register,
        "- `nb77b6d5f092f`　認知戦に弱いリベラルを糾弾する——語る場、翻訳層、決める場を壊される社会（`PENDING`）",
        "- `nb77b6d5f092f`　認知戦に弱いリベラルを糾弾する——語る場、翻訳層、決める場を壊される社会（`PENDING`）\n- `n4940d2f00d0a`　「Emperorだから」では説明できない――日本皇室の重みと、皇室典範改正で国民に見せるべき論点（`PENDING`）",
    )
    replace(
        register,
        "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件（新規・原文先行、PENDING）",
        "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件（新規・原文先行、PENDING）\n- `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`：1件（新規・原文先行、PENDING）",
    )

    operations = "analysis/stabilization_audit/OPERATIONS.md"
    replace(operations, "監査対象の詳細カード：79件", "監査対象の詳細カード：80件")
    replace(operations, "新着・未割り当て等の未解析カード：25件", "新着・未割り当て等の未解析カード：24件")
    replace(operations, "詳細カード79件", "詳細カード80件")
    replace(operations, "新規・原文先行分析4件（PENDING）", "新規・原文先行分析5件（PENDING）")
    replace(operations, "未解析カード25件", "未解析カード24件")

    index = "articles/INDEX.md"
    replace(index, "文脈解析あり：357件", "文脈解析あり：358件")
    replace(index, "文脈未解析・新着：25件", "文脈未解析・新着：24件")
    replace(index, "詳細カード：79件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 4件）", "詳細カード：80件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 5件）")
    replace(index, "未解析カード：25件", "未解析カード：24件")
    replace(index, "詳細カード79件のうち", "詳細カード80件のうち")
    replace(index, "4件は新規・原文先行分析のPENDING", "5件は新規・原文先行分析のPENDING")
    replace(index, "13. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md)\n14. [モデル監査]", "13. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md)\n14. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md)\n15. [モデル監査]")
    replace(index, "15. [バッチ・横断分析監査]", "16. [バッチ・横断分析監査]")
    replace(index, "16. [運用監査]", "17. [運用監査]")
    replace(index, "新規・原文先行カード4件（PENDING）", "新規・原文先行カード5件（PENDING）")

    current = "context/CURRENT.md"
    replace(current, "文脈解析あり：357件", "文脈解析あり：358件")
    replace(current, "未割り当て・新着：25件", "未割り当て・新着：24件")
    replace(current, "詳細カード：79件", "詳細カード：80件")
    replace(current, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
    replace(current, "## 詳細カード79件の割当て", "## 詳細カード80件の割当て")
    replace(current, "- 2026-07-04新規・原文先行：1件\n- 合計：79件", "- 2026-07-04新規・原文先行：1件\n- 2026-07-06新規・原文先行：1件\n- 合計：80件")

    next_path = "context/NEXT.md"
    replace(next_path, "文脈解析あり：357件", "文脈解析あり：358件")
    replace(next_path, "未割り当て・新着：25件", "未割り当て・新着：24件")
    replace(next_path, "詳細カード：79件", "詳細カード：80件")
    replace(next_path, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
    replace(next_path, "- `CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件を新規・原文先行で作成、PENDING", "- `CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件を新規・原文先行で作成、PENDING\n- `CARDS_10_NEW_ANALYSIS_2026-07-06.md`：1件を新規・原文先行で作成、PENDING")
    replace(next_path, "## 直近の新規・原文先行カード\n\n- `nb77b6d5f092f`", "## 直近の新規・原文先行カード\n\n- `n4940d2f00d0a`：男系皇統維持と旧宮家案の選択を手続き中立へ薄めず、愛子内親王殿下を制度の補修材にすることを拒否し、変更の実体を隠して作る民意を民主主義への愚弄として記録\n- `nb77b6d5f092f`")
    replace(next_path, "監査記録：`analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`、", "監査記録：`analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`、`analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`、")
    replace(next_path, "状態：4件とも`PENDING`", "状態：5件とも`PENDING`")

    subprocess.run(
        [
            "git",
            "add",
            "START_HERE.md",
            "analysis/INDIVIDUAL_ARTICLE_REVIEW_PROGRESS.md",
            "analysis/KEY_ARTICLE_SELECTION.md",
            "analysis/STABILIZATION_AUDIT_REGISTER.md",
            "analysis/stabilization_audit/OPERATIONS.md",
            "articles/INDEX.md",
            "context/CURRENT.md",
            "context/NEXT.md",
        ],
        cwd=base.ROOT,
        check=True,
    )


def main() -> int:
    finalize_n494_once()
    coverage = load_json(COVERAGE_PATH)
    articles = coverage.get("articles")
    if not isinstance(articles, dict):
        raise ValueError("COVERAGE.json articles must be an object")

    if not BASELINE_PATH.exists():
        baseline = {
            "created_at": utc_now(),
            "description": "Initial 351-article corpus analyzed through phase bundles or individual cards",
            "note_ids": sorted(articles),
        }
        write_json(BASELINE_PATH, baseline)
        print(f"baseline initialized: {len(articles)} note IDs")
        return 0

    baseline = load_json(BASELINE_PATH)
    baseline_ids_raw = baseline.get("note_ids")
    if not isinstance(baseline_ids_raw, list):
        raise ValueError("BASELINE_NOTE_IDS.json note_ids must be an array")
    baseline_ids = {str(value) for value in baseline_ids_raw}

    coverage_updated_at = str(coverage.get("updated_at") or "")
    reset_ids: list[str] = []
    for note_id, entry in articles.items():
        if note_id in baseline_ids or not isinstance(entry, dict):
            continue
        auto_covered_same_run = (
            entry.get("analysis_state") == "covered"
            and str(entry.get("covered_at") or "") == coverage_updated_at
            and not str(entry.get("role") or "").strip()
        )
        if not auto_covered_same_run:
            continue
        entry.update(
            {
                "analysis_state": "pending",
                "coverage_type": "unassigned",
                "analysis_unit": "unassigned",
                "analysis_label": "新着・未割り当て",
                "analysis_ref": "",
                "covered_content_hash": "",
                "covered_title": "",
                "covered_published_at": "",
                "covered_public_status": "",
                "covered_at": "",
            }
        )
        reset_ids.append(note_id)

    if reset_ids:
        coverage["updated_at"] = utc_now()
        write_json(COVERAGE_PATH, coverage)
    print(f"baseline protected: reset_to_pending={len(reset_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
