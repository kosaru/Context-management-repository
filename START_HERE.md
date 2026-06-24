# START HERE

このリポジトリは、匿名noteの記事本文を再保管するためではなく、記事同士のつながりと、そこから育った思考の文脈を共有するための場所です。

## 正本の切り分け

- 公開中の最新本文：note公開ページ
- 初期コーパスと過去記事目録：noteエクスポート
- 新着・更新・公開状態の差分：定期同期
- 文脈・系譜・現在地：このリポジトリ
- 作業中の解釈：暫定。確認済み事実と混同しない

運用の詳細：

- `docs/INGESTION_WORKFLOW.md`
- `docs/REVIEW_WORKFLOW.md`

## コーパス

- 公開記事：351件
- 期間：2026-01-24〜2026-06-23
- note ID重複：なし
- タイトル欠落：なし
- 本文欠落：なし

## 現在の解析構造

```text
時期別資料束での文脈読解
  → 351 / 351記事

コンパクト記事地図
  → 351 / 351記事

詳細な個別カード
  → 35記事

空の未解析カード
  → 0記事
```

全351記事を長文の個別カードへ変換することは目標にしない。

- 時期別資料束：成立順、試行、修正、合流を読む
- コンパクト地図：全記事の所在、冒頭要旨、接続候補を探す
- 個別カード：転換点、統合稿、修正、反例などを詳しく読む

## 読む順番

1. `context/CURRENT.md`
2. `indexes/CROSS_RECONSTRUCTION.md`
3. `indexes/LINEAGES.md`
4. `indexes/CURRENT_POSITIONS.md`
5. `indexes/THEMES.md`
6. `indexes/CONCEPTS.md`
7. `indexes/QUESTIONS.md`
8. `indexes/UNRESOLVED_QUESTIONS.md`
9. `articles/COMPACT_MAP.md`
10. `articles/INDEX.md`
11. `articles/CROSS_ROLES.md`
12. `analysis/VERTICAL_HORIZONTAL_CROSSCHECK.md`
13. 必要な時期別資料束・個別カード

機械的な全件一覧は `articles/CARD_INDEX.md` を参照する。

---

# 縦読み

時期別解析は、問い・概念・修正が成立した順番を保存する。

- `analysis/PHASE_01_2026-01-24_TO_02-10.md`：74記事
- `analysis/PHASE_02_2026-02-11_TO_02-27.md`：101記事
- `analysis/PHASE_03_2026-03-02_TO_03-13.md`：85記事
- `analysis/PHASE_04_2026-03-14_TO_03-21.md`：29記事
- `analysis/PHASE_05_2026-03-24_TO_03-31.md`：21記事
- `analysis/PHASE_06_2026-03-23_TO_05-01.md`：16記事
- `analysis/PHASE_06_CROSS_RECONSTRUCTION_SUPPLEMENT.md`：第6期の横断後補記

縦読みでは次を区別する。

- 問いの初出
- 試行
- 修正
- 自己整理
- 統合稿
- 一般読者向け再構成
- 後から付いた名称
- 担い手・作用範囲が明確になった段階

後期の完成形を初期記事へ遡及しない。

---

# 横断読み

`indexes/CROSS_RECONSTRUCTION.md`は、異なる領域で反復する構造を整理する。

`indexes/LINEAGES.md`は、全記事を次の六本の幹から読む。

1. 生活が壊れない条件から、人類継続・文明保存・減速へ
2. 社会を止めずに変える――保存・再設計・回転・責任配置
3. 負荷を一人へ集中させない――Security・Comfort・内部条件・退出可能性
4. 倫理と主体を人格から生成構造へ戻す
5. 単線化された説明を、検証可能な場所へ戻す
6. AIとの関係を、答えから読解・修復へ移す

全351記事版へ更新済み：

- `indexes/CURRENT_POSITIONS.md`
- `indexes/THEMES.md`
- `indexes/CONCEPTS.md`
- `indexes/QUESTIONS.md`
- `indexes/UNRESOLVED_QUESTIONS.md`

---

# 全記事コンパクト地図

`articles/COMPACT_MAP.md`を入口とし、時期別の7ファイルへ分けている。

- 全記事：351件
- 詳細な個別カード：35件
- コンパクト地図のみ：316件

地図に含むもの：

- note ID
- 公開日
- タイトル
- 本文冒頭から抽出した暫定要旨
- 役割候補
- 六系譜への接続候補
- 前後の記事
- 時期別解析または個別カードへの参照

冒頭要旨、役割候補、系譜候補は探索用の暫定情報であり、詳細解析ではない。

## 詳細カードへ昇格する条件

- 新しい概念・問いの初出
- 既存系譜を修正・反転させる記事
- 複数系譜が合流する統合稿
- 後続記事の読み方を変える修正・反例・破棄
- 事実と推論の厳密な分離が必要な記事
- コンパクト地図では記事固有の差異が消える記事

本文が「未解析。」だけの空カードは削除し、今後も作らない。

---

# 横断再構築で行った主な補正

## SecurityとComfort

意味変更ではなく、次として固定した。

```text
安心の機能分解
→ 担い手配置
→ 国家によるComfort独占への警戒
→ 一般市場への作用範囲拡張
```

参照：`analysis/SECURITY_COMFORT_ROLE_ALLOCATION.md`

## 社会的事実

```text
複数主体の作用が同方向へ重なる
≠
目的・意図・利害が一致している
```

共謀や意図一致を前提にしない。

## キュゥべえ

有限な合理だけでなく、次を追加した。

- 情報の選択的開示
- 質問可能性の支配
- 近位目的と遠位大義の縫合
- 実質的同意条件
- メディア、生成AI、将来AGI、社会的事実への接続

参照：

- `analysis/KYUBEY_INFORMATION_ASYMMETRY.md`
- `analysis/KYUBEY_MEDIA_AGI_CONNECTIONS.md`

## 縦横照合

`analysis/VERTICAL_HORIZONTAL_CROSSCHECK.md`で、次を区別した。

- 修正が必要な箇所
- 補記だけが必要な箇所
- 成立順の記録として残す箇所

---

# 継続運用

稼働中：

- `scripts/sync_note.py`：note ID単位の増分同期
- `scripts/collect_note_api.py`：完全取得判定つき一覧発見
- `scripts/update_analysis_coverage.py`：解析済み本文ハッシュの台帳
- `scripts/prune_empty_note_cards.py`：空カードだけを安全に削除
- `scripts/build_compact_article_map.py`：全件コンパクト地図の再生成
- `scripts/note_index.py`：記事・解析索引
- `.github/workflows/collect-note.yml`：週次同期・月次全件検証

状態と変更履歴：

- `sources/note/catalog.json`
- `sources/note/change-log.jsonl`
- `sources/note/last-sync.json`
- `analysis/COVERAGE.json`
- `analysis/COVERAGE.md`
- `review/INBOX.md`

新着・変更記事を既存六系譜へ自動回収しない。

```text
差分を検出
→ 公開本文を確認
→ 初出・試行・修正・統合・適用・反例・分岐・破棄を判定
→ 必要な記事だけ詳細カードへ昇格
→ 系譜・現在地への影響を反映
```

## note

- アカウント：<https://note.com/shirokuma1970>
