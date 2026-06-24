# note差分の文脈レビュー運用

更新日：2026-06-24

## 目的

定期同期は、新着・本文変更・タイトル変更・公開状態変更という**差分の存在**を検出する。

しかし、差分が思想・系譜・現在地へどのような意味を持つかは、自動処理では決めない。

```text
同期
  → 現在の公開状態と本文ハッシュを記録

カバレッジ
  → どの本文ハッシュまで、どの解析文書で読んだかを記録

レビュー
  → 現在状態と解析済み状態の差を人間が判定

判定反映
  → 受け入れ・保留・再開をカバレッジへ記録
```

---

# 1．正本関係

## `sources/note/catalog.json`

現在の公開状態の正本。

- 現在のタイトル
- 公開日
- 公開状態
- 本文ハッシュ
- 最終確認時刻
- スナップショットとカードへの参照

## `analysis/COVERAGE.json`

解析済み状態の正本。

- どの本文ハッシュまで読んだか
- どの解析単位で読んだか
- 記事の役割
- 受け入れ時刻
- 責任ある保留の理由・再確認条件

本文が変わっても、`covered_content_hash`は自動更新しない。

## `analysis/COVERAGE.md`

カバレッジの人間向け集計。

個別カードが`unreviewed`でも、時期別資料束で解析済みなら記事全体は`covered`になりうる。

## `review/INBOX.md`

現在の文脈レビュー待ち一覧。

次を表示する。

- 新着・未割り当て
- 解析後の本文変更
- タイトル・公開日変更
- 公開状態変更
- 責任ある保留
- 直近同期の取得失敗

## GitHub Issue「note文脈レビュー待ち」

`review/INBOX.md`に確認対象がある間だけ開く。

確認対象がなくなると自動で閉じる。

---

# 2．記事カード状態とカバレッジ状態を分ける

記事カードの状態は、個別カードの完成度を示す。

```text
unreviewed
proposed
analyzed / reviewed
```

カバレッジ状態は、記事本文が何らかの解析単位で読まれたかを示す。

```text
covered
pending
deferred
```

したがって、

```text
カードがunreviewed
≠
記事全体が未分析
```

である。

初期351記事では、個別カードが未解析でも、第1〜第6期の資料束で文脈解析済みの記事がある。

---

# 3．レビュー対象になる条件

現在の`catalog.json`と、`COVERAGE.json`に保存した受け入れ時点を比較する。

## 新規・未割り当て

- 新しいnote ID
- どの解析単位にも割り当てられていない記事

## 本文変更

```text
catalog.content_hash
≠
coverage.covered_content_hash
```

## タイトル変更

```text
catalog.title
≠
coverage.covered_title
```

## 公開日変更

```text
catalog.published_at
≠
coverage.covered_published_at
```

## 公開状態変更

```text
catalog.public_status
≠
coverage.covered_public_status
```

取得失敗はカバレッジ差分とは別に、直近同期レポートから表示する。

---

# 4．人間が判定する内容

新着・変更を読んだ後、最低限次を決める。

## 4-1．事実上の変更範囲

- 誤字・句読点・リンクだけか
- 表現整理か
- 主語・比較・因果が変わったか
- 留保・不確実性が変わったか
- 中心命題が追加・削除されたか
- 結論が反転したか
- 他記事との関係が変わったか

## 4-2．記事の役割

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

既存系譜に似ているだけで自動的に統合しない。

## 4-3．既存地図への影響

次の更新要否を個別に判断する。

- 記事カード
- `context/CURRENT.md`
- `indexes/LINEAGES.md`
- `indexes/CURRENT_POSITIONS.md`
- `indexes/THEMES.md`
- `indexes/CONCEPTS.md`
- `indexes/QUESTIONS.md`
- `indexes/UNRESOLVED_QUESTIONS.md`
- 時期別・追加解析文書

## 4-4．抵抗点

既存六系譜へ接続できる点だけでなく、接続すると消える差異を確認する。

```text
既存概念を補強する部分
＋
既存概念を壊す部分
＋
まだ接続できない部分
```

を分ける。

---

# 5．判定の三つの操作

`.github/workflows/apply-note-review-decision.yml`を手動実行する。

ワークフロー名：`Apply note review decision`

## accept

差分の確認と必要な文脈更新が終わった場合に使う。

入力：

- `note_id`
- `analysis_ref`
- `coverage_type`
- `role`

### `analysis_ref`

今回の本文状態を受け入れた根拠となる解析文書。

例：

```text
articles/cards/2026-07-01-nxxxx.md
analysis/PHASE_07_2026-07.md
analysis/NEW_BRANCH_ANALYSIS.md
```

正本カードが存在する場合は省略できる。

### `coverage_type`

- `individual_card`
- `phase_bundle`
- `cross_index`
- `other`

### `role`

記事の役割を入力する。

例：

```text
初出
修正
統合稿
適用稿
反例
分岐
破棄
```

acceptすると、現在の本文ハッシュ・タイトル・公開日・公開状態が解析済み基準へ進む。

## defer

現時点では結論を固定しないが、放置もしない場合に使う。

必須：

- `note_id`
- `defer_reason`

必要に応じて：

- `recheck_after`
- `recheck_condition`

例：

```text
defer_reason:
一次資料が未確認で、系譜への位置づけを固定できない

recheck_after:
2026-07-15

recheck_condition:
公式報告書または元資料が公開されたとき
```

これは曖昧な保留ではない。

```text
保留理由
＋
再確認時期
＋
再確認条件
```

を持つ「責任ある保留」である。

## reopen

保留条件が満たされた、または判定をやり直す場合に使う。

入力：

- `note_id`

deferredからpendingへ戻し、再びレビュー対象にする。

---

# 6．ワークフロー実行後

`Apply note review decision`は次を行う。

1. 入力を検証する。
2. `scripts/update_analysis_coverage.py`へ判定を渡す。
3. `analysis/COVERAGE.json`を更新する。
4. `analysis/COVERAGE.md`を再生成する。
5. `review/INBOX.md`を再生成する。
6. 変更をGitへコミットする。
7. GitHub Issueを更新する。
8. 確認対象がゼロならIssueを閉じる。

同期の差分ログや過去のカバレッジ履歴を削除しない。

---

# 7．ローカルでの判定反映

## accept

```bash
python scripts/update_analysis_coverage.py \
  --accept nxxxxxxxxxxxx \
  --analysis-ref articles/cards/2026-07-01-nxxxxxxxxxxxx.md \
  --coverage-type individual_card \
  --role 修正
```

## defer

```bash
python scripts/update_analysis_coverage.py \
  --defer nxxxxxxxxxxxx \
  --defer-reason "一次資料が未確認" \
  --recheck-after 2026-07-15 \
  --recheck-condition "公式資料が公開されたとき"
```

## reopen

```bash
python scripts/update_analysis_coverage.py \
  --reopen nxxxxxxxxxxxx
```

## 再生成だけ行う

```bash
python scripts/update_analysis_coverage.py
```

---

# 8．現在の状態

初期351記事はすべてカバレッジ済みである。

```text
台帳登録：351
文脈解析済み：351
未割り当て：0
責任ある保留：0
再確認対象：0
```

今後は、新着または受け入れ後の変更だけがレビューキューへ入る。

---

# 9．運用上の禁止事項

- 同期処理だけで`covered_content_hash`を進めない。
- 新着記事を既存六系譜へ自動分類しない。
- 本文変更をすべて思想変更と扱わない。
- 軽微変更を理由に記事カード全体を作り直さない。
- 保留理由なしにdeferしない。
- 再確認条件のない長期保留を常態化しない。
- Issueを閉じるためだけにacceptしない。
- 既存体系へ合わない部分をノイズとして捨てない。
