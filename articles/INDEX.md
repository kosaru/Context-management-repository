# 記事索引

## 収集元

- note：<https://note.com/shirokuma1970>

## 状態

- [x] RSS収集スクリプトの追加
- [x] GitHub Actionsから手動実行できる状態
- [x] 最新5記事のURLと本文スナップショット取得
- [x] 最初の5記事の記事カード作成
- [x] 最初の5記事でカード形式を検証
- [ ] 全記事への展開
- [ ] テーマ・問い・概念・系譜の横断索引作成

## 記事カード一覧

この範囲は `scripts/collect_note.py` が更新する。解析済みカードは収集スクリプトで上書きしない。

<!-- AUTO-GENERATED-ARTICLES:START -->
| 公開日 | 記事 | 状態 | note |
|---|---|---|---|
| 2026-06-23 | [予算委員会は誰のものかー一つの音声断片が、週刊誌・国会・メディア・AIを通って「事実」になるまで](cards/2026-06-23-nee567e7bf172.md) | analyzed | [公開本文](https://note.com/shirokuma1970/n/nee567e7bf172) |
| 2026-06-21 | [話が飛んでいるようで、飛んでいないー具象を包摂し、上位概念を組み替える思考](cards/2026-06-21-n9189519559b6.md) | analyzed | [公開本文](https://note.com/shirokuma1970/n/n9189519559b6) |
| 2026-06-20 | [型をそのままにするな、技を切り離したままにするな](cards/2026-06-20-n8608abc16b0e.md) | analyzed | [公開本文](https://note.com/shirokuma1970/n/n8608abc16b0e) |
| 2026-06-20 | [複雑さを知ることは、防御になる](cards/2026-06-20-n11cae8fdcf99.md) | analyzed | [公開本文](https://note.com/shirokuma1970/n/n11cae8fdcf99) |
| 2026-06-20 | [活性酸素を悪者にすると、身体の循環が見えなくなる](cards/2026-06-20-n3f1b99d428b4.md) | analyzed | [公開本文](https://note.com/shirokuma1970/n/n3f1b99d428b4) |
<!-- AUTO-GENERATED-ARTICLES:END -->

## 運用

記事カードは `articles/cards/` に置く。

公開本文はnoteを正本とし、カードには必ず次を含める。

- 記事タイトル
- 公開日
- note URL
- 出発点となる問い
- 中心命題
- 論理の流れ
- 維持した文脈
- 新しく押し広げた点
- 棄却した読み
- 未解決の問い
- 関連記事

カードの形式は `templates/article-card.md` を使う。
