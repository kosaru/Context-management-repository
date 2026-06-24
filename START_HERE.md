# START HERE

このリポジトリは、匿名noteの記事本文を再保管するためではなく、記事同士のつながり、そこから育った思考、今後の更新判断を共有するための場所です。

## 正本の切り分け

- 公開中の最新本文：note公開ページ
- 初期コーパスと過去記事目録：noteエクスポート
- 新着・更新・公開状態の差分：定期同期
- 文脈・系譜・現在地・選定判断：このリポジトリ
- 作業中の解釈：暫定。確認済み事実と混同しない

運用の詳細：

- `docs/INGESTION_WORKFLOW.md`
- `docs/REVIEW_WORKFLOW.md`

## コーパスと解析構造

- 公開記事：351件
- 対象期間：2026-01-24〜2026-06-23
- 時期別資料束で文脈読解済み：351件
- コンパクト地図へ掲載：351件
- 詳細な個別カード：35件
- 空の未解析カード：0件

```text
時期別資料束
  → 成立順、試行、修正、合流を読む

コンパクト記事地図
  → 全記事の所在、冒頭要旨、接続候補を探す

詳細な個別カード
  → 転換点、統合稿、修正、反例を記事単位で詳しく読む
```

全351記事を長文カードへ変換することは目標にしない。

## 現在の段階

```text
第A段階：収集と初期解析
  → 完了

第B段階：縦読み・横断再構築
  → 完了

第B-2段階：重要記事の選定と詳細カードへの昇格
  → 現在の作業

第C段階：新着・更新の継続運用
  → 稼働中

第D段階：未解決問題から理論・制度・記事を作る
  → 準備稿。未開始
```

## 現在の作業

残る316記事を公開日順に埋めない。

横断再構築によって重要性が見えた記事だけを選び、必要なものを35件の詳細カードへ追加する。

選定順：

1. 現在の立場を成立させた転換点
2. 以前の立場を修正した記事
3. 複数系譜の接続点
4. 現在の体系へ抵抗する記事
5. 未解決問題を進めるために必要な記事

参照：

- `context/NEXT.md`
- `roadmaps/PHASE_B2_KEY_ARTICLE_SELECTION.md`
- `analysis/KEY_ARTICLE_SELECTION.md`（次に作成）

## 第D段階との関係

次期研究プログラムは準備稿として保持する。

- `roadmaps/PHASE_D_CONTINUITY_WITHOUT_SACRIFICE.md`
- `research/CONTINUITY_DESIGN_KERNEL.md`

ただし、現在の作業ではない。

```text
重要記事を選ぶ
→ 記事単位で根拠・修正・抵抗点を確認する
→ 必要な詳細カードを増やす
→ 六系譜・現在地・未解決問題を必要に応じて修正する
→ 第D段階へ進む
```

## 読む順番

1. `context/CURRENT.md`
2. `context/NEXT.md`
3. `roadmaps/PHASE_B2_KEY_ARTICLE_SELECTION.md`
4. `indexes/CROSS_RECONSTRUCTION.md`
5. `indexes/LINEAGES.md`
6. `indexes/CURRENT_POSITIONS.md`
7. `indexes/THEMES.md`
8. `indexes/CONCEPTS.md`
9. `indexes/QUESTIONS.md`
10. `indexes/UNRESOLVED_QUESTIONS.md`
11. `articles/COMPACT_MAP.md`
12. `articles/INDEX.md`
13. `articles/CROSS_ROLES.md`
14. 必要な時期別資料束・個別カード
15. 将来準備として `roadmaps/PHASE_D_CONTINUITY_WITHOUT_SACRIFICE.md`

## 六系譜

1. 生活が壊れない条件から、人類継続・文明保存・減速へ
2. 社会を止めずに変える――保存・再設計・回転・責任配置
3. 負荷を一人へ集中させない――Security・Comfort・内部条件・退出可能性
4. 倫理と主体を人格から生成構造へ戻す
5. 単線化された説明を、検証可能な場所へ戻す
6. AIとの関係を、答えから読解・修復へ移す

## 継続運用

稼働中：

- `scripts/sync_note.py`：note ID単位の増分同期
- `scripts/update_analysis_coverage.py`：解析済み本文ハッシュの台帳
- `scripts/prune_empty_note_cards.py`：空カードだけを安全に削除
- `scripts/build_compact_article_map.py`：全件コンパクト地図の再生成
- `.github/workflows/collect-note.yml`：週次同期・月次全件検証

新着・変更記事も既存六系譜へ自動回収しない。

```text
差分を検出
→ 公開本文を確認
→ 初出・試行・修正・統合・適用・反例・分岐・破棄を判定
→ 必要な記事だけ詳細カードへ昇格
→ 系譜・現在地への影響を反映
```

## note

- アカウント：<https://note.com/shirokuma1970>
