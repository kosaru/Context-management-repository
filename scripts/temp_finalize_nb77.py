#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def edit(path: str, replacements: list[tuple[str, str]]) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"pattern not found in {path}: {old!r}")
        text = text.replace(old, new, 1)
    target.write_text(text, encoding="utf-8")


run(
    "python3", "scripts/update_analysis_coverage.py",
    "--accept", "nb77b6d5f092f",
    "--analysis-ref", "articles/cards/2026-07-04-nb77b6d5f092f.md",
    "--coverage-type", "individual_card",
    "--role", "認知戦の入口と効果・翻訳層の自壊",
)
run("python3", "scripts/note_index.py")

edit("START_HERE.md", [
    ("さらに新規・原文先行カード3件を作成した。", "さらに新規・原文先行カード4件を作成した。"),
    ("- 文脈解析あり：356件", "- 文脈解析あり：357件"),
    ("- 個別カードあり：104件（詳細カード78件＋未解析カード26件）", "- 個別カードあり：104件（詳細カード79件＋未解析カード25件）"),
    ("- 新規・原文先行分析：3件（PENDING）", "- 新規・原文先行分析：4件（PENDING）"),
    ("12. `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`\n13. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n14. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n15. `analysis/stabilization_audit/OPERATIONS.md`", "12. `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`\n13. `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n14. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n15. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n16. `analysis/stabilization_audit/OPERATIONS.md`"),
])

edit("analysis/INDIVIDUAL_ARTICLE_REVIEW_PROGRESS.md", [
    ("- 詳細カード：78件", "- 詳細カード：79件"),
    ("- `PENDING`：3件（新規・原文先行）", "- `PENDING`：4件（新規・原文先行）"),
    ("- 未解析カード：26件", "- 未解析カード：25件"),
    ("## 詳細カード78件の割当て", "## 詳細カード79件の割当て"),
    ("| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md` |\n| 合計 | 78 |", "| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md` |\n| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md` |\n| 合計 | 79 |"),
])

edit("analysis/KEY_ARTICLE_SELECTION.md", [
    ("- 詳細カード：78件", "- 詳細カード：79件"),
    ("- 新規・原文先行分析：3件（PENDING）", "- 新規・原文先行分析：4件（PENDING）"),
    ("詳細カード78件は、次の監査台帳へ記録した。", "詳細カード79件は、次の監査台帳へ記録した。"),
    ("- `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`\n", "- `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`\n- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n"),
])

edit("analysis/STABILIZATION_AUDIT_REGISTER.md", [
    ("既存監査由来の詳細カード75件と、新規・原文先行カード3件を管理する。", "既存監査由来の詳細カード75件と、新規・原文先行カード4件を管理する。"),
    ("- 新規・原文先行分析・ユーザー確認待ち：3件", "- 新規・原文先行分析・ユーザー確認待ち：4件"),
    ("## 個別カード78件の現在地", "## 個別カード79件の現在地"),
    ("- `PENDING`：3件", "- `PENDING`：4件"),
    ("3件は新規・原文先行分析のユーザー確認待ち", "4件は新規・原文先行分析のユーザー確認待ち"),
    ("## 新規・原文先行分析3件", "## 新規・原文先行分析4件"),
    ("- `ncdb4235f58bf`　批判で終わるなと言った以上、私は何を再設計してきたのか（`PENDING`）\n", "- `ncdb4235f58bf`　批判で終わるなと言った以上、私は何を再設計してきたのか（`PENDING`）\n- `nb77b6d5f092f`　認知戦に弱いリベラルを糾弾する——語る場、翻訳層、決める場を壊される社会（`PENDING`）\n"),
    ("- `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`：1件（新規・原文先行、PENDING）\n", "- `analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`：1件（新規・原文先行、PENDING）\n- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件（新規・原文先行、PENDING）\n"),
])

edit("analysis/stabilization_audit/OPERATIONS.md", [
    ("監査対象の詳細カード：78件", "監査対象の詳細カード：79件"),
    ("新着・未割り当て等の未解析カード：26件", "新着・未割り当て等の未解析カード：25件"),
    ("- 詳細カード78件", "- 詳細カード79件"),
    ("- 新規・原文先行分析3件（PENDING）", "- 新規・原文先行分析4件（PENDING）"),
    ("- 未解析カード26件", "- 未解析カード25件"),
])

edit("articles/INDEX.md", [
    ("- 文脈解析あり：356件", "- 文脈解析あり：357件"),
    ("- 文脈未解析・新着：26件", "- 文脈未解析・新着：25件"),
    ("- 詳細カード：78件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 3件）", "- 詳細カード：79件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 4件）"),
    ("- 未解析カード：26件", "- 未解析カード：25件"),
    ("詳細カード78件のうち、74件は改稿候補・ユーザー確認待ち、1件は使用停止、3件は新規・原文先行分析のPENDINGです。", "詳細カード79件のうち、74件は改稿候補・ユーザー確認待ち、1件は使用停止、4件は新規・原文先行分析のPENDINGです。"),
    ("12. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md)\n13. [モデル監査]", "12. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md)\n13. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md)\n14. [モデル監査]"),
    ("14. [バッチ・横断分析監査]", "15. [バッチ・横断分析監査]"),
    ("15. [運用監査]", "16. [運用監査]"),
    ("- 新規・原文先行カード3件（PENDING）", "- 新規・原文先行カード4件（PENDING）"),
])

edit("context/CURRENT.md", [
    ("- 文脈解析あり：356件", "- 文脈解析あり：357件"),
    ("- 未割り当て・新着：26件", "- 未割り当て・新着：25件"),
    ("- 詳細カード：78件", "- 詳細カード：79件"),
    ("- 新規・原文先行分析：3件（PENDING）", "- 新規・原文先行分析：4件（PENDING）"),
    ("## 詳細カード78件の割当て", "## 詳細カード79件の割当て"),
    ("- 2026-07-03新規・原文先行：2件\n- 合計：78件", "- 2026-07-03新規・原文先行：2件\n- 2026-07-04新規・原文先行：1件\n- 合計：79件"),
])

edit("context/NEXT.md", [
    ("- 文脈解析あり：356件", "- 文脈解析あり：357件"),
    ("- 未割り当て・新着：26件", "- 未割り当て・新着：25件"),
    ("- 詳細カード：78件", "- 詳細カード：79件"),
    ("- 新規・原文先行分析：3件（PENDING）", "- 新規・原文先行分析：4件（PENDING）"),
    ("- `CARDS_08_NEW_ANALYSIS_2026-07-03.md`：1件を新規・原文先行で作成、PENDING\n", "- `CARDS_08_NEW_ANALYSIS_2026-07-03.md`：1件を新規・原文先行で作成、PENDING\n- `CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件を新規・原文先行で作成、PENDING\n"),
    ("## 直近の新規・原文先行カード\n\n- `ncdb4235f58bf`", "## 直近の新規・原文先行カード\n\n- `nb77b6d5f092f`：認知戦を偽情報の問題へ閉じず、入口と効果を分け、現代リベラルが内部純度競争によって翻訳層を自壊させる構造と再設計命令を記録\n- `ncdb4235f58bf`"),
    ("- 監査記録：`analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`、", "- 監査記録：`analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`、`analysis/stabilization_audit/CARDS_08_NEW_ANALYSIS_2026-07-03.md`、"),
    ("- 状態：3件とも`PENDING`", "- 状態：4件とも`PENDING`"),
])
