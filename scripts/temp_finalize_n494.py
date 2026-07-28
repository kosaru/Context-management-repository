from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing expected text in {path}: {old!r}")
    p.write_text(text.replace(old, new), encoding="utf-8")


# START_HERE.md
replace("START_HERE.md", "新規・原文先行カード4件を作成した", "新規・原文先行カード5件を作成した")
replace("START_HERE.md", "文脈解析あり：357件", "文脈解析あり：358件")
replace("START_HERE.md", "個別カードあり：104件（詳細カード79件＋未解析カード25件）", "個別カードあり：104件（詳細カード80件＋未解析カード24件）")
replace("START_HERE.md", "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
replace(
    "START_HERE.md",
    "13. `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n14. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n15. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n16. `analysis/stabilization_audit/OPERATIONS.md`",
    "13. `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n14. `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`\n15. `analysis/stabilization_audit/MODELS_AND_INDEXES.md`\n16. `analysis/stabilization_audit/BATCHES_AND_CROSS.md`\n17. `analysis/stabilization_audit/OPERATIONS.md`",
)

# Progress
p = "analysis/INDIVIDUAL_ARTICLE_REVIEW_PROGRESS.md"
replace(p, "詳細カード：79件", "詳細カード：80件")
replace(p, "`PENDING`：4件（新規・原文先行）", "`PENDING`：5件（新規・原文先行）")
replace(p, "未解析カード：25件", "未解析カード：24件")
replace(p, "## 詳細カード79件の割当て", "## 詳細カード80件の割当て")
replace(
    p,
    "| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md` |\n| 合計 | 79 |",
    "| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md` |\n| 新規・原文先行 | 1 | `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md` |\n| 合計 | 80 |",
)

# Key article selection
p = "analysis/KEY_ARTICLE_SELECTION.md"
replace(p, "詳細カード：79件", "詳細カード：80件")
replace(p, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
replace(p, "詳細カード79件は、次の監査台帳へ記録した。", "詳細カード80件は、次の監査台帳へ記録した。")
replace(
    p,
    "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`",
    "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`\n- `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`",
)

# Register
p = "analysis/STABILIZATION_AUDIT_REGISTER.md"
replace(p, "新規・原文先行カード4件を管理する", "新規・原文先行カード5件を管理する")
replace(p, "新規・原文先行分析・ユーザー確認待ち：4件", "新規・原文先行分析・ユーザー確認待ち：5件")
replace(p, "## 個別カード79件の現在地", "## 個別カード80件の現在地")
replace(p, "`PENDING`：4件", "`PENDING`：5件")
replace(p, "4件は新規・原文先行分析のユーザー確認待ち", "5件は新規・原文先行分析のユーザー確認待ち")
replace(p, "## 新規・原文先行分析4件", "## 新規・原文先行分析5件")
replace(
    p,
    "- `nb77b6d5f092f`　認知戦に弱いリベラルを糾弾する——語る場、翻訳層、決める場を壊される社会（`PENDING`）",
    "- `nb77b6d5f092f`　認知戦に弱いリベラルを糾弾する——語る場、翻訳層、決める場を壊される社会（`PENDING`）\n- `n4940d2f00d0a`　「Emperorだから」では説明できない――日本皇室の重みと、皇室典範改正で国民に見せるべき論点（`PENDING`）",
)
replace(
    p,
    "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件（新規・原文先行、PENDING)",
    "- `analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件（新規・原文先行、PENDING)\n- `analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`：1件（新規・原文先行、PENDING)",
)

# Operations
p = "analysis/stabilization_audit/OPERATIONS.md"
replace(p, "監査対象の詳細カード：79件", "監査対象の詳細カード：80件")
replace(p, "新着・未割り当て等の未解析カード：25件", "新着・未割り当て等の未解析カード：24件")
replace(p, "詳細カード79件", "詳細カード80件")
replace(p, "新規・原文先行分析4件（PENDING）", "新規・原文先行分析5件（PENDING）")
replace(p, "未解析カード25件", "未解析カード24件")

# Articles index
p = "articles/INDEX.md"
replace(p, "文脈解析あり：357件", "文脈解析あり：358件")
replace(p, "文脈未解析・新着：25件", "文脈未解析・新着：24件")
replace(p, "詳細カード：79件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 4件）", "詳細カード：80件（改稿候補74件＋使用停止1件＋新規・原文先行PENDING 5件）")
replace(p, "未解析カード：25件", "未解析カード：24件")
replace(p, "詳細カード79件のうち", "詳細カード80件のうち")
replace(p, "4件は新規・原文先行分析のPENDING", "5件は新規・原文先行分析のPENDING")
replace(
    p,
    "13. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md)\n14. [モデル監査]",
    "13. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md)\n14. [新規・原文先行カード1件](../analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md)\n15. [モデル監査]",
)
replace(p, "15. [バッチ・横断分析監査]", "16. [バッチ・横断分析監査]")
replace(p, "16. [運用監査]", "17. [運用監査]")
replace(p, "新規・原文先行カード4件（PENDING）", "新規・原文先行カード5件（PENDING）")

# Current context
p = "context/CURRENT.md"
replace(p, "文脈解析あり：357件", "文脈解析あり：358件")
replace(p, "未割り当て・新着：25件", "未割り当て・新着：24件")
replace(p, "詳細カード：79件", "詳細カード：80件")
replace(p, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
replace(p, "## 詳細カード79件の割当て", "## 詳細カード80件の割当て")
replace(p, "- 2026-07-04新規・原文先行：1件\n- 合計：79件", "- 2026-07-04新規・原文先行：1件\n- 2026-07-06新規・原文先行：1件\n- 合計：80件")

# Next context
p = "context/NEXT.md"
replace(p, "文脈解析あり：357件", "文脈解析あり：358件")
replace(p, "未割り当て・新着：25件", "未割り当て・新着：24件")
replace(p, "詳細カード：79件", "詳細カード：80件")
replace(p, "新規・原文先行分析：4件（PENDING）", "新規・原文先行分析：5件（PENDING）")
replace(
    p,
    "- `CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件を新規・原文先行で作成、PENDING",
    "- `CARDS_09_NEW_ANALYSIS_2026-07-04.md`：1件を新規・原文先行で作成、PENDING\n- `CARDS_10_NEW_ANALYSIS_2026-07-06.md`：1件を新規・原文先行で作成、PENDING",
)
replace(
    p,
    "## 直近の新規・原文先行カード\n\n- `nb77b6d5f092f`",
    "## 直近の新規・原文先行カード\n\n- `n4940d2f00d0a`：男系皇統維持と旧宮家案の選択を手続き中立へ薄めず、愛子内親王殿下を制度の補修材にすることを拒否し、変更の実体を隠して作る民意を民主主義への愚弄として記録\n- `nb77b6d5f092f`",
)
replace(
    p,
    "監査記録：`analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`、",
    "監査記録：`analysis/stabilization_audit/CARDS_10_NEW_ANALYSIS_2026-07-06.md`、`analysis/stabilization_audit/CARDS_09_NEW_ANALYSIS_2026-07-04.md`、",
)
replace(p, "状態：4件とも`PENDING`", "状態：5件とも`PENDING`")
