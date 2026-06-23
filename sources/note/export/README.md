# noteエクスポート正規化コーパス

このディレクトリは、noteのエクスポートXMLを記事単位へ正規化した機械可読コーパスを置く。

## 収録範囲

- 公開記事：351本
- 期間：2026-01-24〜2026-06-23
- 既存解析カードと一致：25本
- 新規解析対象：326本

## ファイル

- `manifest.json`：本文を除く全記事メタデータ
- `YYYY-MM-partNN.jsonl`：本文Markdownを含む記事データ

JSONLの各行は1記事で、次のフィールドを持つ。

```json
{
  "note_id": "n...",
  "title": "...",
  "note_url": "https://note.com/...",
  "published_at": "YYYY-MM-DD HH:MM:SS",
  "updated_at": "YYYY-MM-DD HH:MM:SS",
  "status": "publish",
  "post_type": "post",
  "content_hash": "sha256...",
  "image_count": 0,
  "body_markdown": "..."
}
```

## 正本の扱い

- 公開中の最新本文：note公開ページ
- 初期全体分析の入力：この正規化コーパス
- 文脈・系譜・現在地：GitHub上の記事カードと索引
- 新着・更新検出：全体分析完了後の定期スクレイピング

## 注意

- 原本XMLはGit履歴へ保存しない。
- 画像本体はこのコーパスに含めず、本文中の参照だけを保持する。
- エクスポート日時点の本文であり、公開ページの後日の修正とは差が生じうる。
- 解析済みカードは本文更新だけで自動上書きしない。
