# 安定化監査台帳

更新日：2026-06-25

## 現在の扱い

既存の詳細カード73件、時期別解析、横断分析、派生モデルは、元文章の強度保持を確認していない。

- 強度監査通過：0件
- 改稿候補・ユーザー確認待ち：1件
- 個別カード73件：再監査対象
- 時期別解析・横断分析・モデル：再監査対象
- 新しいB群解析：停止

## 個別カード73件の一次洗い出し

- `CONFIRMED`：2件
- `REWRITTEN-PENDING-USER`：1件
- `HIGH-RISK`：67件
- `PENDING`：3件
- `PASSED`：0件

HIGH-RISKは最終判定ではない。既存カードの構造・表現・編集経緯から、元文章を弱めた可能性を具体的に指摘した状態である。

## リスク記号

- `R1` 拒否を条件付き許容へ変えた
- `R2` 非対称性を役割分担へ均した
- `R3` 名指しした主体の責任を市場・一般構造へ移した
- `R4` 構造的抽象化を事実命題として慎重化した
- `R5` 未解決の緊張をモデル・段階・表へ閉じた
- `R6` 後期体系を初期記事へ遡及した
- `R7` 提供者・制度側の責任を利用者の使い方へ移した
- `R8` 名指しした政治的主体を無名の相互作用へ一般化した
- `R9` 呼びかけ・告発・エールを抽象理論へ変えた
- `R10` 原文にない極端な反対読みを棄却対象として追加した
- `R11` 不確実性の注記で強い推論まで弱めた
- `R12` 矛盾・撤回・飛躍を発展史へ整えた
- `R13` 強い表現を柔らかい機能語へ置き換えた
- `R14` 目的・意図・利害の区別を過剰適用した

## 分割台帳

- `analysis/stabilization_audit/CARDS_01_LATE.md`：25件
- `analysis/stabilization_audit/CARDS_02_FORMATION_AND_METHOD.md`：17件
- `analysis/stabilization_audit/CARDS_03_RESPONSIBILITY_CONTINUITY_AI.md`：18件
- `analysis/stabilization_audit/CARDS_04_POLITICS_AND_B_GROUP.md`：13件
- `analysis/stabilization_audit/MODELS_AND_INDEXES.md`
- `analysis/stabilization_audit/BATCHES_AND_CROSS.md`
- `analysis/stabilization_audit/OPERATIONS.md`

## 確認済みの安定化

- `nee567e7bf172`：社会的事実・企業利益・意図の区別を過剰適用し、元文章の構造批判を弱めた
- `ne5105ace2279`：OpenAIの設計思想への批判を、市場圧力と意図未確認へ移した
- `ndcca526034cf`：世界そのものへの拒否を、負担管理の条件へ変えた。カード全面改稿、派生B群分析撤回、派生モデル使用停止まで実施。ユーザー確認待ち

## 監査方法

- `analysis/STABILIZATION_AUDIT_METHOD.md`
- `templates/article-card-strength-audit.md`

カードの存在・内容記入と、強度監査通過を分ける。PASSEDになるまで信頼済み分析として扱わない。
