# START HERE

このリポジトリは、匿名noteの記事本文を再保管するためではなく、記事同士のつながり、そこから育った思考、今後の更新判断を共有するための場所です。

## 正本の切り分け

- 公開中の最新本文：note公開ページ
- 初期コーパスと過去記事目録：noteエクスポート
- 新着・更新・公開状態の差分：定期同期
- 文脈・系譜・現在地・選定判断：このリポジトリ
- 作業中の解釈：暫定。確認済み事実と混同しない

## コーパスと解析構造

- 公開記事：351件
- 対象期間：2026-01-24〜2026-06-23
- 時期別資料束で文脈読解済み：351件
- コンパクト地図へ掲載：351件
- 詳細な個別カード：67件
- コンパクト地図のみ：284件
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

第B-2段階：一次選定30件の詳細カード化
  → 完了

第B-3段階：B群・抵抗記事の再判定
  → 現在の作業

第C段階：新着・更新の継続運用
  → 稼働中

第D段階：未解決問題から理論・制度・記事を作る
  → 準備稿。未開始
```

## 一次選定30件の詳細化

5バッチで完了した。

1. 方法論：7件
2. 責任／決定／退出：7件
3. 継続／文明／Security：6件
4. AI／情報／Repair：5件
5. 政治機能／国際秩序：5件

詳細カードは35件から65件へ増加した。

## B群再判定1――AI企業の方向

2記事を詳細カードへ昇格した。

- `n9ebf441f85ab`　AIはどこに入り込もうとしているのか
- `ne5105ace2279`　OpenAIはポピュリズムに寄っているのではないか

### 残した独自層

```text
AI Repair
→ 対話内部の誤読・安定化・関係修復

AI製品統治
→ 応答特性がどの評価・市場・事業回路で選ばれるか
```

### 批評時の分離

```text
観測されたAI出力
→ 公開された製品変更
→ 推定される設計評価指標
→ 市場・事業上の報酬
→ 企業利益・組織制約
→ 企業・設計者の意図
```

出力から意図へ直接飛ばない。

ただし意図が未確認でも、企業が変更可能で、反復効果を予見でき、利用者が回避できない設計には説明責任が残る。

## 現在の主要モデル

1. `indexes/RESPONSIBILITY_MODEL.md`
2. `indexes/CONTINUITY_MODEL.md`
3. `indexes/AI_REPAIR_MODEL.md`
4. `indexes/AI_PRODUCT_GOVERNANCE_MODEL.md`
5. `indexes/ORDER_RENEGOTIATION_MODEL.md`

これらは完成理論ではない。記事群から抽出した仮置きであり、B群・抵抗記事によって修正される可能性がある。

## 次の作業

B-06「二項対立とAI」の3記事を再判定する。

- `n360b7b29f068`
- `nd77d3ea83d56`
- `necfb29c22f74`

```text
二項対立を思考道具として使う
と
二項対立へ居付く
を分ける

対立を消さない
と
AIが双方を均衡化して論点を薄める
を分ける
```

## 読む順番

1. `context/CURRENT.md`
2. `context/NEXT.md`
3. `analysis/KEY_ARTICLE_SELECTION.md`
4. `analysis/INDIVIDUAL_ARTICLE_REVIEW_PROGRESS.md`
5. `analysis/B_GROUP_01_AI_COMPANY_DIRECTION.md`
6. `indexes/AI_PRODUCT_GOVERNANCE_MODEL.md`
7. `analysis/BATCH_04_AI_INFORMATION_REPAIR.md`
8. `indexes/AI_REPAIR_MODEL.md`
9. `analysis/BATCH_05_POLITICAL_FUNCTIONS_INTERNATIONAL_ORDER.md`
10. `indexes/ORDER_RENEGOTIATION_MODEL.md`
11. `indexes/CROSS_RECONSTRUCTION.md`
12. `indexes/LINEAGES.md`
13. `indexes/CURRENT_POSITIONS.md`
14. `indexes/UNRESOLVED_QUESTIONS.md`
15. `articles/COMPACT_MAP.md`
16. `articles/INDEX.md`
17. 必要な時期別資料束・個別カード

## 六系譜

1. 生活が壊れない条件から、人類継続・文明保存・減速へ
2. 社会を止めずに変える――保存・再設計・回転・責任配置
3. 負荷を一人へ集中させない――Security・Comfort・内部条件・退出可能性
4. 倫理と主体を人格から生成構造へ戻す
5. 単線化された説明を、検証可能な場所へ戻す
6. AIとの関係を、答えから読解・修復・製品統治へ移す

## 継続運用

- `scripts/sync_note.py`：note ID単位の増分同期
- `scripts/update_analysis_coverage.py`：解析済み本文ハッシュの台帳
- `scripts/refresh_card_coverage.py`：本文変更がない詳細カードだけ解析参照を安全に昇格
- `scripts/prune_empty_note_cards.py`：空カードだけを安全に削除
- `scripts/build_compact_article_map.py`：全件コンパクト地図の再生成
- `.github/workflows/collect-note.yml`：週次同期・月次全件検証・カード変更時の索引更新

新着・変更記事も既存六系譜へ自動回収しない。

## note

- アカウント：<https://note.com/shirokuma1970>
