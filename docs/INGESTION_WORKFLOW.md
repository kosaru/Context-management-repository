# note記事の取り込み・更新運用

更新日：2026-06-24

## 目的

この運用は、note本文をGitHubへ複製して正本化するものではない。

```text
note公開ページ
  = 公開中の最新本文の正本

noteエクスポート
  = 初期コーパスと過去記事目録の基準

定期同期
  = 新着・本文変更・タイトル変更・公開状態の差分検出

GitHub
  = 記事カード、系譜、現在地、概念、問い、変更履歴の正本
```

初期351記事の縦読み・横断再構築は完了した。

以後は、新しい記事や公開本文の変更を、既存の文脈へ自動的に回収せず、差分として受け取る。

---

# 1．主キー

## note IDを唯一の主キーにする

記事の同一性は、ファイル名、タイトル、公開日ではなくnote IDで判断する。

```text
https://note.com/shirokuma1970/n/<note_id>
```

公開日は、API、RSS、エクスポート、タイムゾーン処理によって1日ずれる場合がある。

そのため、

```text
公開日が違う
≠
別記事
```

である。

## 重複時の優先順位

同じnote IDのカードが複数ある場合は、次を優先する。

```text
analyzed / reviewed
→ proposed
→ unreviewed
```

解析済みカードと未解析の自動生成カードが重複した場合、解析済みカードを残す。

複数の解析済みカードがある場合は自動削除せず、人間確認対象として記録する。

---

# 2．実装ファイル

## 同期本体

`scripts/sync_note.py`

役割：

- 既存スナップショットから状態目録を初期化する
- creator APIから公開記事一覧を取得する
- note IDで既存目録と照合する
- 新規・更新候補だけ本文ページを取得する
- 本文ハッシュを比較する
- 新規記事だけ未解析カードを作る
- 解析済みカードを上書きしない
- 公開一覧から消えた候補を記録する
- 同期レポートと変更ログを出力する

## 一覧発見

`scripts/collect_note_api.py`

役割：

- note creator APIのページネーション
- note ID、URL、タイトル、公開日時、更新日時の取得
- 取得が完全に終了したかの判定
- API失敗時のRSSフォールバック

RSSは直近記事だけの窓であり、全件一覧ではない。

したがってRSSフォールバック時は、記事の削除・非公開化を判定しない。

## 本文抽出

`scripts/collect_note.py`

役割：

- 公開ページから本文を抽出する
- 本文スナップショットを書く
- 新規の未解析カードを作る

定期運用では直接起動せず、`sync_note.py`から抽出機能を利用する。

## カード索引

`scripts/note_index.py`

役割：

- note ID単位で正本カードを選ぶ
- `articles/CARD_INDEX.md`を生成する

`articles/INDEX.md`は人間向けの全体案内であり、自動処理では上書きしない。

## 重複整理

`scripts/dedupe_note_cards.py`

役割：

- 同じnote IDの未解析重複カードを削除する
- 複数の保護対象カードは削除せず、診断ファイルへ記録する
- 機械カード索引を再生成する

---

# 3．状態目録

## `sources/note/catalog.json`

記事単位の継続状態を保持する。

主な項目：

```text
note_id
title
note_url
published_at
source_updated_at
first_seen_at
last_seen_at
last_checked_at
content_hash
public_status
snapshot_path
card_path
analysis_status
```

## 時刻の意味

- `first_seen_at`：この運用が記事を初めて認識した時刻
- `last_seen_at`：公開一覧で最後に確認した時刻
- `last_checked_at`：本文ページを最後に取得してハッシュ確認した時刻
- `source_updated_at`：note APIが示す更新日時
- `last_status_change_at`：公開状態候補が変化した時刻

## 公開状態

通常は次を使う。

- `public`
- `missing_from_public_index`

`missing_from_public_index`は削除・非公開の確定ではない。

次の可能性を含む。

- 非公開化
- 削除
- creator APIの仕様変更
- ページネーション異常
- 一時的取得失敗
- アカウント側の表示条件変更

完全なcreator API取得が確認できた場合にだけ記録する。

RSSフォールバック、件数制限付き実行、不完全なページネーションでは記録しない。

---

# 4．差分記録

## `sources/note/change-log.jsonl`

変更があった実行だけ、1イベント1行のJSONとして追記する。

イベント種別：

### `new`

新しいnote IDを発見した。

処理：

- 本文スナップショットを追加
- 未解析カードを追加
- 状態目録へ追加

### `body_changed`

既存記事の本文ハッシュが変わった。

処理：

- 取得時スナップショットを最新公開本文で更新
- 変更前後のハッシュを記録
- 解析済みカードは変更しない
- 人間が論旨への影響を確認する

旧スナップショットはGit履歴に残る。

### `metadata_changed`

タイトル、URL、公開日、更新日時などが変わったが、本文ハッシュは変わらなかった。

処理：

- スナップショットのメタデータを更新
- 記事カードは自動変更しない

### `missing_from_public_index`

完全な公開一覧取得で、以前存在したnote IDが見つからなかった。

処理：

- 削除しない
- 状態目録と変更ログへ候補として記録
- 公開URLを手動確認する

## 書かないイベント

月次の全件検証で本文が同一だった記事は、変更ログへ追記しない。

同期レポートの取得件数だけに残す。

---

# 5．同期レポート

## `sources/note/last-sync.json`

直近実行の状態を保持する。

主な項目：

```text
complete_discovery
verify_all
bootstrapped_catalog_records
discovered_count
seen_note_ids
fetched_count
source_changed_count
metadata_change_count
new_card_count
missing_from_public_index_count
events_written
failure_count
failures
```

## 完全取得の条件

`complete_discovery`がtrueになるのは、次をすべて満たす場合だけである。

- creator APIを使用した
- 明示的な最終ページ、または空ページまで到達した
- `--limit 0`で実行した

最大ページ数への到達や重複ページによる中断は、完全取得としない。

---

# 6．通常同期と全件検証

## 通常同期

通常実行では、本文ページを取得する対象を次に限定する。

- 新しいnote ID
- スナップショットがない記事
- タイトル、URL、公開日が変わった記事
- API更新日時が前回から変わった記事

その他の記事は、一覧上の存在だけを確認して`last_seen_at`を更新する。

## 全件検証

`--verify-all`では、発見した全記事の本文ページを取得し、本文ハッシュを比較する。

用途：

- API更新日時が取得できない場合の補完
- 抽出処理の変化確認
- note側のサイレント修正確認
- 状態目録と公開本文の定期整合性確認

全件検証でも、本文が同一ならスナップショットを書き換えない。

---

# 7．GitHub Actions

`.github/workflows/collect-note.yml`

## 定期実行

### 週次同期

毎週日曜日12時17分ごろ（日本時間）。

- 公開一覧を確認
- 新着・更新候補だけ本文取得
- 状態目録を更新

### 月次全件検証

毎月1日12時47分ごろ（日本時間）。

- 全公開記事の本文ハッシュを確認
- サイレント修正を検出
- 変更がない記事は記録を増やさない

GitHub Actionsのcronは混雑等で遅れる場合がある。

## 手動実行

`workflow_dispatch`で次を指定できる。

- `limit`
- `max_pages`
- `verify_all`

`limit`を指定した実行では、公開一覧から消えた記事の判定をしない。

## コミット対象

自動処理がコミットするもの：

- `sources/note/catalog.json`
- `sources/note/change-log.jsonl`
- `sources/note/last-sync.json`
- `sources/note/discovery.json`
- `sources/note/card-deduplication.json`
- 新規・更新された本文スナップショット
- 新規の未解析カード
- `articles/CARD_INDEX.md`

自動処理がコミットしないもの：

- `articles/INDEX.md`
- 解析済みカードの本文
- `context/CURRENT.md`
- 系譜、テーマ、概念、問い
- 時期別解析文書

---

# 8．人間による差分判定

本文変更を検出しても、すべてを思想上の変更として扱わない。

## 軽微変更

- 誤字
- 句読点
- 見出し
- リンク
- 読みやすさの調整
- 意味を変えない言い換え

対応：

- スナップショットと変更ログだけでよい
- 記事カード・系譜は更新しない

## 文脈へ影響する変更

- 中心命題の追加・削除
- 主語、比較、因果の変更
- 留保や不確実性の追加・削除
- 調査結果による事実関係の訂正
- 結論の反転
- 他記事との関係変更

対応：

1. 公開本文の差分を確認する
2. 記事カードへ「公開後の変更」を追記する
3. 初出・修正・統合・破棄の役割を判定する
4. 必要な系譜・概念・問いだけを更新する
5. `context/CURRENT.md`への影響を確認する

---

# 9．新規記事の文脈判定

新規記事を既存六系譜へ自動的に分類しない。

次の役割を先に判定する。

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
- 反例
- 分岐
- 破棄

既存系譜へ似ているだけで回収すると、新しい問いや矛盾が消える。

```text
既存概念に接続できるか
＋
既存概念を壊す部分はないか
```

を同時に見る。

---

# 10．失敗時の扱い

## creator API失敗

RSSへフォールバックする。

ただし、RSSは全件一覧ではないため、

- 非公開化候補を作らない
- 全件取得成功と扱わない
- `discovery.json`へAPIエラーを残す

## 一部本文取得失敗

- 成功した記事の状態は更新する
- 失敗した記事を`last-sync.json`へ列挙する
- 既存スナップショットとカードを削除しない

## 全本文取得失敗

同期スクリプトは失敗終了する。

自動取得失敗を「変更なし」や「全件確認済み」と扱わない。

## 重複カード

未解析カードだけなら自動削除する。

解析済み・提案済みカードが複数ある場合は失敗終了し、人間確認を求める。

---

# 11．ローカル実行

## 通常同期

```bash
python scripts/sync_note.py \
  --profile https://note.com/shirokuma1970 \
  --limit 0 \
  --max-pages 100
```

## 全件検証

```bash
python scripts/sync_note.py \
  --profile https://note.com/shirokuma1970 \
  --limit 0 \
  --max-pages 100 \
  --verify-all
```

## 重複整理

```bash
python scripts/dedupe_note_cards.py
```

## カード索引再生成

```bash
python scripts/note_index.py
```

---

# 12．継続運用の完了条件

各実行で次を満たす。

- 発見方法と完全取得可否を記録した
- 新着・本文変更・メタデータ変更を区別した
- 非公開化候補を不完全一覧から作っていない
- 新規記事のスナップショットとカードを追加した
- 解析済みカードを上書きしていない
- note ID単位で重複を整理した
- 失敗を変更なしと誤認していない
- 文脈更新が必要な差分を人間確認へ残した
