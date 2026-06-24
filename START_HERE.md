# START HERE

このリポジトリは、匿名noteの記事本文を再保管するためではなく、記事同士のつながりと、そこから育った思考の文脈を共有するための場所です。

## 正本の切り分け

- 公開中の最新本文の正本：note公開ページ
- 初期コーパスと記事目録の基準：noteエクスポート
- 新着・更新・公開状態の差分検出：定期同期
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

1. `context/CURRENT.md`
2. `indexes/CROSS_RECONSTRUCTION.md`
3. `indexes/LINEAGES.md`
4. `indexes/CURRENT_POSITIONS.md`
5. `indexes/THEMES.md`
6. `indexes/CONCEPTS.md`
7. `indexes/QUESTIONS.md`
8. `indexes/UNRESOLVED_QUESTIONS.md`
9. `articles/CROSS_ROLES.md`
10. `analysis/VERTICAL_HORIZONTAL_CROSSCHECK.md`
11. `analysis/EXPORT_CORPUS_OVERVIEW.md`
12. `analysis/PHASE_01_...` から `analysis/PHASE_06_...`
13. 必要に応じて記事カード
14. 機械的な全カード一覧は `articles/CARD_INDEX.md`

## 縦読みと横断読み

### 縦読み

時期別解析は、問い・概念・修正が成立した順番を保存する。

- `analysis/PHASE_01_2026-01-24_TO_02-10.md`：74記事
- `analysis/PHASE_02_2026-02-11_TO_02-27.md`：101記事
- `analysis/PHASE_03_2026-03-02_TO_03-13.md`：85記事
- `analysis/PHASE_04_2026-03-14_TO_03-21.md`：29記事
- `analysis/PHASE_05_2026-03-24_TO_03-31.md`：21記事
- `analysis/PHASE_06_2026-03-23_TO_05-01.md`：16記事
- `analysis/PHASE_06_CROSS_RECONSTRUCTION_SUPPLEMENT.md`：第6期の横断後補記
- `analysis/SECURITY_COMFORT_ROLE_ALLOCATION.md`：SecurityとComfortの役割配置を補正

時期別解析では、次を区別している。

- 問いの初出
- 試行
- 修正
- 自己整理
- 統合稿
- 一般読者向け再構成
- 後から付いた名称
- 担い手・作用範囲が明確になった段階

### 横断読み

`indexes/CROSS_RECONSTRUCTION.md`は、351記事を時期から切り離し、異なる領域で反復する構造を索引化する。

1. 最上位目的と下位目的
2. 思考の基本運動
3. 社会機能と担い手
4. 反復する故障構造
5. 修復・帰還・再開の構造
6. スケールをまたぐ対応関係
7. 記事の役割
8. 概念の変化類型
9. 未解決の緊張
10. 縦読み索引の更新候補

`indexes/LINEAGES.md`は、横断再構築を六本の幹へまとめる。

1. 生活が壊れない条件から、人類継続・文明保存・減速へ
2. 社会を止めずに変える――保存・再設計・回転・責任配置
3. 負荷を一人へ集中させない――Security・Comfort・内部条件・退出可能性
4. 倫理と主体を人格から生成構造へ戻す
5. 単線化された説明を、検証可能な場所へ戻す
6. AIとの関係を、答えから読解・修復へ移す

`articles/CROSS_ROLES.md`は、初回25記事を次の役割で位置づけ直す。

- 初出
- 試行
- 衝突記録
- 修正
- 自己整理
- 統合稿
- 一般読者向け再構成
- 適用稿
- 方法論化
- 運用設計

`analysis/VERTICAL_HORIZONTAL_CROSSCHECK.md`は、縦読みと横断読みを照合し、次を区別する。

- 修正が必要な箇所
- 補記だけが必要な箇所
- 成立順の記録としてそのまま残す箇所

後から見えた体系を初期記事へ遡及して書き込まず、誤読だけを限定的に修正する。

## 横断索引の更新状況

- `indexes/CROSS_RECONSTRUCTION.md`：全記事版初版を作成済み
- `indexes/LINEAGES.md`：全351記事版へ更新済み
- `indexes/CURRENT_POSITIONS.md`：全351記事版へ更新済み
- `indexes/THEMES.md`：全351記事版へ更新済み
- `indexes/CONCEPTS.md`：全351記事版へ更新済み
- `indexes/QUESTIONS.md`：全351記事版へ更新済み
- `indexes/UNRESOLVED_QUESTIONS.md`：全351記事版へ更新済み
- `articles/CROSS_ROLES.md`：既存25記事の横断役割を作成済み
- `articles/INDEX.md`：全351記事版の管理構造へ更新済み
- `articles/CARD_INDEX.md`：note ID単位の機械索引を生成済み
- `analysis/VERTICAL_HORIZONTAL_CROSSCHECK.md`：縦横照合済み

## 横断再構築で行った補正

### SecurityとComfort

意味変更ではなく、次として固定した。

```text
機能分解
→ 担い手配置
→ 国家によるComfort独占への警戒
→ 一般市場への作用範囲拡張
```

### 社会的事実

```text
作用が同方向へ重なる
≠
目的・意図・利害が一致している
```

と修正した。

各主体の共謀や意図一致を前提にしない。

### キュゥべえ

有限な合理だけでなく、次を追加した。

- 情報の選択的開示
- 質問可能性の支配
- 近位目的と遠位大義の縫合
- 実質的同意条件
- メディア、生成AI、将来AGI、社会的事実への接続

### 重複カード

note IDを主キーとし、公開日だけが異なる4件の未解析重複カードを削除した。

## 現在の作業

### フェーズA：全体分析

完了。

- エクスポートXMLの構造・件数確認
- 351記事と既存25記事のnote ID照合
- 351記事の時期別・個別解析

### フェーズB：横断再構築

完了。

- 横断再構築インデックス
- 六系譜
- 既存25記事の横断役割
- 現在の立場
- テーマ、概念、問い、未解決問題
- 個別カードの必要補正
- 第6期の横断後補記
- 記事索引と重複カード整理
- 縦読みと横断読みの最終照合

### フェーズC：継続運用

稼働開始済み。

実装：

- `scripts/sync_note.py`：note ID単位の増分同期
- `scripts/collect_note_api.py`：完全取得判定つき一覧発見
- `scripts/note_index.py`：機械カード索引
- `scripts/dedupe_note_cards.py`：重複カード整理
- `.github/workflows/collect-note.yml`：週次同期・月次全件検証

状態・変更記録：

- `sources/note/catalog.json`
- `sources/note/change-log.jsonl`
- `sources/note/last-sync.json`
- `sources/note/discovery.json`
- `sources/note/card-deduplication.json`

初回同期結果：

- creator APIで351記事を最終ページまで確認
- 完全取得：成功
- 本文取得失敗：0件
- 本文変更：0件
- 公開一覧から消えた候補：0件
- 新規記事：0件
- 重複・曖昧カード：0件
- 公開日のメタデータ差異：4件

4件はいずれも以前から確認していた1日ずれで、本文ハッシュは同一だった。

公開日が変わっても解析済みカードを自動改名・上書きせず、公開メタデータは状態目録と機械索引、解析内容は既存カードで管理する。

新記事を既存六系譜へ自動回収せず、初出、試行、修正、統合、適用、反例、分岐、破棄を判定する。

## エクスポート原本について

原本XMLはGit履歴へ入れていない。

リポジトリには、検査結果、正規化スクリプト、解析文書を保存している。

- `sources/note/export/manifest.json`
- `sources/note/export/README.md`
- `scripts/import_note_export.py`

## 現在の到達点

- エクスポート収録351記事を初回解析済み
- 第1〜第6解析単位を作成済み
- 後期記事の多くが初出ではなく、前史を統合した再構成稿であることを確認済み
- 全351記事版の六系譜を再構築済み
- 既存25記事を、統合稿・適用稿・方法論化などへ位置づけ直し済み
- 現在の立場、テーマ、概念、問い、未解決問題を全351記事版へ更新済み
- 縦読みと横断読みを照合し、必要な補正を反映済み
- 横断再構築フェーズを完了
- 増分同期・変更記録・定期実行を実装し、初回同期を検証済み
- 今後は新着・更新差分が出た時点で文脈判定を行う

## note

- アカウント：<https://note.com/shirokuma1970>
