# START HERE

このリポジトリは、匿名noteの記事本文を再保管するためではなく、記事同士のつながりと、そこから育った思考の文脈を共有するための場所です。

## 正本の切り分け

- 公開中の最新本文の正本：note公開ページ
- 初期コーパスと記事目録の基準：noteエクスポート
- 新着・更新・公開状態の差分検出：定期スクレイピング
- 文脈・関係・現在地の正本：このリポジトリ
- 作業中の解釈：暫定。確定事項と混同しない

詳しい運用は `docs/INGESTION_WORKFLOW.md` を参照する。

## エクスポートで確定した範囲

ユーザー提供のnoteエクスポートXMLから次を確認した。

- 公開記事：351本
- 期間：2026-01-24〜2026-06-23
- 初回取得25記事との一致：25本
- note ID重複：なし
- タイトル欠落：なし
- 本文欠落：なし

351記事すべてを、時期別資料束または個別記事カードのいずれかへ入れ、初回の全体解析を完了した。

全体の初期所見は `analysis/EXPORT_CORPUS_OVERVIEW.md` を参照する。

## 全体の文脈を読む順番

全記事版の横断索引を再構築中は、次の順番で読む。

1. `context/CURRENT.md`
2. `analysis/EXPORT_CORPUS_OVERVIEW.md`
3. `analysis/PHASE_01_...` から `analysis/PHASE_06_...`
4. `indexes/CURRENT_POSITIONS.md`
5. `indexes/LINEAGES.md`
6. 必要に応じて横断索引と記事カード

## 時期別解析

- `analysis/PHASE_01_2026-01-24_TO_02-10.md`：74記事
- `analysis/PHASE_02_2026-02-11_TO_02-27.md`：101記事
- `analysis/PHASE_03_2026-03-02_TO_03-13.md`：85記事
- `analysis/PHASE_04_2026-03-14_TO_03-21.md`：29記事
- `analysis/PHASE_05_2026-03-24_TO_03-31.md`：21記事
- `analysis/PHASE_06_2026-03-23_TO_05-01.md`：残り16記事
- `analysis/SECURITY_COMFORT_ROLE_ALLOCATION.md`：SecurityとComfortの役割配置を補正

時期別解析では、全記事を同じ重さで要約していない。

- 問いの初出
- 試行
- 修正
- 自己整理
- 統合稿
- 一般読者向け再構成
- 後から付いた名称
- 担い手・作用範囲が明確になった段階

を区別している。

## 現在の横断索引

以下は初回取得25記事をもとに作った暫定版であり、全351記事版へ更新中である。

- `indexes/THEMES.md`
- `indexes/CONCEPTS.md`
- `indexes/QUESTIONS.md`
- `indexes/UNRESOLVED_QUESTIONS.md`
- `indexes/CURRENT_POSITIONS.md`
- `indexes/LINEAGES.md`
- `articles/INDEX.md`

## 現在の作業

### フェーズA：全体分析

1. エクスポートXMLの構造・件数確認。完了。
2. 351記事と既存25記事のnote ID照合。完了。
3. 351記事の時期別・個別解析。完了。
4. 既存25記事カードの起点・前史・役割を修正する。
5. 5本の暫定系譜を、全351記事版へ再構築する。
6. 現在の立場、テーマ、概念、問い、未解決問題を更新する。

### フェーズB：継続運用

全体索引の再構築後、定期スクレイピングで次を追加する。

- 新着記事
- 公開本文の変更
- タイトル・公開状態の変更
- 既存目録との差分

スクレイピング結果で解析済みカードを自動上書きしない。note IDを主キーにし、公開日の差による重複カードを作らない。

## エクスポート原本について

原本XMLはGit履歴へ入れていない。

リポジトリには、検査結果、正規化スクリプト、解析文書を保存している。

- `sources/note/export/manifest.json`
- `sources/note/export/README.md`
- `scripts/import_note_export.py`

## 現在の到達点

- エクスポート収録351記事を初回解析済み
- 第1〜第6解析単位を作成済み
- 既存25記事カードを個別解析済み
- 後期記事の多くが初出ではなく、前史を統合した再構成稿であることを確認済み
- 保存・再設計・回転、文明保存、Security・Comfort、責任配置、翻訳層、AI稽古論の形成過程を確認済み
- 全351記事版の系譜・索引再構築へ移行
- 全体索引完成後の定期スクレイピング運用方針は確定済み

## note

- アカウント：<https://note.com/shirokuma1970>
