# note文脈レビュー運用

## 目的

このディレクトリは、noteの新着・本文変更・公開状態変更を、既存の文脈へ反映する前の確認場所である。

`articles/cards`の`unreviewed`件数とは分けて扱う。

初期351記事のうち326記事は個別カード未解析だが、第1〜第6期の時期別資料束で文脈解析済みである。

```text
個別カードがunreviewed
≠
記事が文脈上未分析
```

## 正本

- 初期解析済み集合：`analysis/BASELINE_NOTE_IDS.json`
- 現在の公開状態・本文ハッシュ：`sources/note/catalog.json`
- どの本文まで解析したか：`analysis/COVERAGE.json`
- 人間向けカバレッジ概要：`analysis/COVERAGE.md`
- 現在の確認待ち：`review/INBOX.md`
- 判断用テンプレート：`review/DECISION_TEMPLATE.md`

初期基準集合に含まれないnote IDは、公開日が過去であっても自動的に旧フェーズへ割り当てない。

## レビュー対象

`INBOX.md`には次だけを出す。

- 新しいnote ID
- 解析後に本文ハッシュが変わった記事
- 解析後にタイトル・公開日が変わった記事
- 公開一覧から消えた候補
- 直近同期の取得失敗
- 責任ある保留として残した項目

既存の時期別解析でカバー済みの記事は、個別カードが`unreviewed`でも確認待ちにしない。

## 判定すること

新着・変更を読んだ後、次を分ける。

1. 今回すぐ更新するもの
2. 記事の役割
3. 接続する既存系譜
4. 新しい分岐・反例・破棄の有無
5. 今回は決めずに保留するもの
6. 保留理由、再確認時期、再確認条件

記事の役割候補：

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

## GitHub画面から判断を反映する

GitHub Actionsの **Apply note review decision** を手動実行する。

入力項目：

- `action`：`accept` / `defer` / `reopen`
- `note_id`
- `analysis_ref`
- `coverage_type`
- `role`
- `defer_reason`
- `recheck_after`
- `recheck_condition`

ワークフローは次を更新してコミットする。

- `analysis/COVERAGE.json`
- `analysis/COVERAGE.md`
- `review/INBOX.md`

記事カードや系譜の本文は自動変更しない。必要な文脈文書を先に更新してから、最後に判断を反映する。

## 解析済みとして受け入れる

現在の公開本文を読み、必要なカード・系譜・概念・問いを更新した後に実行する。

GitHub Actionsでは：

```text
action = accept
note_id = 対象ID
analysis_ref = articles/cards/... または indexes/...
coverage_type = individual_card / cross_index / phase_bundle / other
role = 修正 / 反例 / 統合稿 など
```

ローカルでは：

```bash
python scripts/update_analysis_coverage.py \
  --accept <NOTE_ID> \
  --analysis-ref articles/cards/<CARD>.md \
  --coverage-type individual_card \
  --role "修正"
```

これにより、現在の本文ハッシュが`covered_content_hash`へ進む。

自動同期だけでは進まない。

## 責任ある保留

今すぐ結論を出さない場合も、単なる放置にしない。

GitHub Actionsでは：

```text
action = defer
defer_reason = 一次資料の確認が必要
recheck_after = 2026-07-01
recheck_condition = 公的資料が公開されたら再確認
```

ローカルでは：

```bash
python scripts/update_analysis_coverage.py \
  --defer <NOTE_ID> \
  --defer-reason "一次資料の確認が必要" \
  --recheck-after "2026-07-01" \
  --recheck-condition "公的資料が公開されたら再確認"
```

保留中に本文や公開状態がさらに変わった場合、その差分も`INBOX.md`へ表示される。

## 保留を再開する

GitHub Actionsでは`action = reopen`を選ぶ。

ローカルでは：

```bash
python scripts/update_analysis_coverage.py --reopen <NOTE_ID>
```

## キューを再生成する

```bash
python scripts/update_analysis_coverage.py
```

定期同期でも自動実行される。

## してはいけないこと

- 新着記事を自動的に既存六系譜へ押し込む
- 過去日付だからという理由で旧フェーズへ回収する
- 本文変更時に`covered_content_hash`を自動更新する
- 解析済みカードをスクレイピング結果で上書きする
- 保留理由・再確認条件なしに確認待ちから消す
- 公開一覧から消えただけで削除・非公開を確定する
