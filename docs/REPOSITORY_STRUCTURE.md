# リポジトリ構成

この文書は、`Context-management-repository` の現在の構成と、各ファイル・ディレクトリの役割を確認するための案内である。

この文書自体は、ユーザー思想の正本でも、記事内容の正本でもない。

リポジトリ内のどこに何があり、どこから原文・監査記録・仮置きの整理へ辿ればよいかを示すための**構造案内**として使う。

リポジトリの運用思想については `context/REPOSITORY_SOIL.md`、現在の作業状態については `START_HERE.md` と `context/NEXT.md` を確認する。

---

## 1．最初に区別するもの

このリポジトリには、性質の違う資料が同居している。

少なくとも次を同じものとして扱わない。

```text
原文・取得時スナップショット
監査記録・事故記録
記事カード
横断分析・時期別分析
索引・派生モデル
現在の作業文脈
レビュー待ち・保留
運用手順・自動処理
```

カード、分析、索引、モデルが存在することは、その内容がユーザー確認済みであることを意味しない。

`REWRITTEN-PENDING-USER` は承認済みではない。

`PASSED` がないものを、ユーザー思想の確定版として扱わない。

原文と後続整理が衝突した場合の扱いは、`README.md`、`START_HERE.md`、`context/REPOSITORY_SOIL.md`、各監査記録の指示に従う。

---

## 2．ルート直下

現在の主な構成は次のとおり。

```text
.github/
AGENTS.md
README.md
START_HERE.md
analysis/
articles/
context/
docs/
indexes/
research/
review/
roadmaps/
scripts/
sources/
templates/
tests/
requirements.txt
```

### `README.md`

リポジトリ全体の入口。

このリポジトリを正本辞書として扱わないこと、原文・AI補助線・安定化の疑いを分けること、`PASSED` の扱い、禁止事項など、参照時の基本原則を置いている。

### `START_HERE.md`

現在の運用状態、監査の入口、正本の優先順位、探索用資料などをまとめた現在地の案内。

件数や監査進捗のように変化する情報は、構造説明であるこの文書へ複製せず、`START_HERE.md` や機械生成上の正本を確認する。

### `AGENTS.md`

このリポジトリを扱うエージェント向けの追加指示。

記事の読み方、壊してはいけない切り分け、更新時の原則などを置いている。

### `requirements.txt`

リポジトリ内のPythonスクリプトが利用する依存関係。

### `.github/`

GitHub側の自動処理を置く場所。

現在は `workflows/` があり、GitHub Actions のワークフローを格納している。

---

## 3．原文と記事単位の資料

### `sources/`

取得した原文側の資料を置く。

現在は `sources/note/` があり、note記事のスナップショットや公開状態を追うための資料が置かれている。

個別記事の内容を確認するとき、記事カードだけで判断せず、まず原文または取得時スナップショットへ戻る。

### `articles/`

記事単位の探索・整理を置く。

現在の主な要素は次のとおり。

```text
articles/cards/
  個別記事カード

articles/maps/
  記事探索用のマップ

articles/CARD_INDEX.md
  カード索引・カバレッジ確認の入口

articles/COMPACT_MAP.md
  コンパクトな探索用マップ

articles/INDEX.md
  記事側の索引

articles/CROSS_ROLES.md
  記事間を横断する役割整理
```

`articles/cards/` のカードは原文に従属する。

`COMPACT_MAP.md`、`maps/`、`CARD_INDEX.md` などは所在確認・探索に使えるが、それだけで記事の強度やユーザーの現在位置を確定しない。

---

## 4．横断整理・監査・カバレッジ

### `analysis/`

時期別分析、バッチ分析、横断分析、カバレッジ、安定化監査などを置く。

主な種類は次のとおり。

```text
analysis/PHASE_*.md
  時期別解析

analysis/BATCH_*.md
  複数記事をまたぐ分析束

analysis/B_GROUP_*.md
  特定の横断テーマ・再検討群

analysis/COVERAGE.md
analysis/COVERAGE.json
  解析カバレッジ

analysis/STABILIZATION_AUDIT_METHOD.md
analysis/STABILIZATION_AUDIT_REGISTER.md
  安定化監査の方法と台帳

analysis/stabilization_audit/
  カード、横断分析、モデルなどの監査・修復記録

analysis/incidents/
  重大な変形事故の記録
```

横断分析は、複数の原文を読むための補助線であり、原文より上位の正本として使わない。

安定化監査を伴う対象では、分析本文だけでなく、対応する `analysis/stabilization_audit/` と `analysis/incidents/` も確認する。

### `indexes/`

概念、問い、系譜、テーマ、現在地、派生モデルなどの横断索引を置く。

たとえば次のようなファイルがある。

```text
CONCEPTS.md
QUESTIONS.md
LINEAGES.md
THEMES.md
CURRENT_POSITIONS.md
CROSS_RECONSTRUCTION.md
*_MODEL.md
```

索引は、原文へ戻るための入口である。

`CURRENT_POSITIONS.md`、`CROSS_RECONSTRUCTION.md`、`CONCEPTS.md`、`QUESTIONS.md`、`LINEAGES.md` などを単独でユーザー思想の確定版として使わない。

---

## 5．現在の文脈

### `context/`

現在の作業文脈と、リポジトリをどう扱うかの運用思想を置く。

現在の主なファイルは次のとおり。

```text
context/CURRENT.md
  現在地を記録する文書

context/NEXT.md
  次に読むもの、現在の作業、直近の監査状態

context/REPOSITORY_SOIL.md
  リポジトリを「固定された思想体系」ではなく「思考の土壌」として扱う運用思想

context/AI_RESPONSE_DECLARATION_2026-09-05.md
  AI応答に関する宣言・運用文脈
```

現在地を確認するときも、ここに書かれた整理を原文より上位へ置かない。

---

## 6．取り込み・レビュー・運用

### `docs/`

リポジトリ運用の説明文書を置く。

現在は次がある。

```text
docs/INGESTION_WORKFLOW.md
  note記事の取り込み・更新運用

docs/REVIEW_WORKFLOW.md
  レビュー運用

docs/REPOSITORY_STRUCTURE.md
  この文書。リポジトリ構成の案内
```

### `review/`

noteの新着、本文変更、公開状態変更などを既存文脈へ反映する前の確認場所。

現在の主な要素は次のとおり。

```text
review/INBOX.md
  現在の確認待ち

review/DECISION_TEMPLATE.md
  判断用テンプレート

review/README.md
  レビュー運用の説明

review/NOTE_EXPORT_DIFF_*.md
review/PENDING_NOTE_IMPORT_*.md
  差分・保留記録
```

`review/` は、未処理だから内容が未分析である、という意味ではない。既存の時期別解析やカバレッジと分けて確認する。

### `scripts/`

note取得・同期、カードやマップ生成、カバレッジ更新、監査スキャンなどの自動処理を置く。

現在は、たとえば次の処理がある。

```text
collect_note*.py
sync_note.py
import_note_export.py
note_index.py
build_compact_article_map.py
build_stabilization_audit_scan.py
update_analysis_coverage.py
refresh_card_coverage.py
sync_review_issue.py
```

処理内容を確認するときは、ファイル名だけで判断せずスクリプト本体と対応する `docs/` の運用文書を読む。

### `templates/`

記事カード作成・監査用テンプレートを置く。

現在は `article-card.md` と `article-card-strength-audit.md` がある。

新規カード・再監査では、現在の運用指示とテンプレートの状態を確認して使う。

### `tests/`

運用スクリプトのテストを置く。

現在は `test_note_context_ops.py` がある。

---

## 7．研究・ロードマップ

### `research/`

既存記事カードや索引とは別に、研究・設計上の検討を置く領域。

現在は `CONTINUITY_DESIGN_KERNEL.md` がある。

ここにある文書も、存在するだけでユーザー確認済みの確定思想にはならない。本文中の状態表示と参照元を確認する。

### `roadmaps/`

作業や検討フェーズのロードマップを置く。

現在は、たとえば次がある。

```text
PHASE_B2_KEY_ARTICLE_SELECTION.md
PHASE_D_CONTINUITY_WITHOUT_SACRIFICE.md
```

ロードマップは作業計画・検討経路であり、原文やユーザー判断を置き換えない。

---

## 8．目的別の入口

### 個別の記事について確認する

```text
sources/
→ articles/cards/
→ 必要なら analysis/stabilization_audit/
→ 必要なら indexes/ や analysis/ の横断資料
```

原文から始め、カードや横断整理は後から照合する。

### 現在どこまで作業しているか確認する

```text
START_HERE.md
context/NEXT.md
analysis/COVERAGE.md
articles/CARD_INDEX.md
review/INBOX.md
```

数値や状態は更新時点が異なる場合があるため、それぞれの更新日と正本指定を確認する。

### リポジトリの運用思想を確認する

```text
README.md
context/REPOSITORY_SOIL.md
AGENTS.md
```

### 安定化事故・読み違いを確認する

```text
analysis/STABILIZATION_AUDIT_METHOD.md
analysis/STABILIZATION_AUDIT_REGISTER.md
analysis/incidents/
analysis/stabilization_audit/
```

### 新着記事・変更記事を処理する

```text
docs/INGESTION_WORKFLOW.md
review/README.md
docs/REVIEW_WORKFLOW.md
review/INBOX.md
```

---

## 9．大まかな関係

```text
note公開本文
    ↓ 取得・差分検出
sources/
    ↓ 原文確認
articles/cards/
    ↓ 必要に応じて監査
analysis/stabilization_audit/
analysis/incidents/
    ↓ 探索・横断参照
indexes/
analysis/
    ↓ 現在の作業文脈
context/

取り込み・レビュー手順 ─ docs/
確認待ち・保留       ─ review/
自動処理             ─ scripts/ + .github/workflows/
テンプレート         ─ templates/
テスト               ─ tests/
研究・設計検討       ─ research/
作業ロードマップ     ─ roadmaps/
```

この図は上下関係を意味しない。

特に、`indexes/` や `analysis/` が `sources/` より上位の正本になる、という意味ではない。

---

## 10．この文書の更新方針

この文書は**構成の案内**に限定する。

記事件数、カード件数、PASSED件数、現在のレビュー件数など、頻繁に変わる状態値は原則として持たない。

それらは `START_HERE.md`、`analysis/COVERAGE.md`、`analysis/COVERAGE.json`、`articles/CARD_INDEX.md`、`review/INBOX.md` など、それぞれの正本・運用文書を確認する。

トップレベルのディレクトリ追加・削除、主要な役割変更、入口となる文書の変更があった場合は、この文書も更新する。
