# 20_data_model_sqlite — SQLite データモデル（ETL内部）

このドキュメントは ETL 内部のストレージ（SQLite）仕様です。  
**CORE は SQLite に依存してはいけません**（取り込み契約は JSONL + manifest のみ）。

## 保存場所（推奨）
- `data/db/normalized.sqlite`

## テーブル設計（最小案）
### cards（正規化カード情報）
- `cid` INTEGER PRIMARY KEY（Konami ID）
- `name_en` TEXT NOT NULL DEFAULT ''
- `card_text_en` TEXT NOT NULL DEFAULT ''
- `name_ja` TEXT NOT NULL DEFAULT ''
- `card_text_ja` TEXT NOT NULL DEFAULT ''
- `card_info_en_json` TEXT NOT NULL DEFAULT ''  （JSON文字列）
- `card_info_ja_json` TEXT NOT NULL DEFAULT ''  （JSON文字列）
- `image_relpath` TEXT NOT NULL DEFAULT ''
- `fetched_at` TEXT NOT NULL DEFAULT ''         （ISO8601）
- `source_json` TEXT NOT NULL DEFAULT ''        （JSON文字列）

> ポイント：日本語は後追い取得のため、初期から `name_ja` / `card_text_ja` を持つ（空文字OK）。

## upsert 方針（冪等性）
- `cid` をキーに INSERT or UPDATE（UPSERT）
- 同じ入力を再実行しても結果が安定すること
- `fetched_at` は「取り込んだ時刻」で更新して良い（データ差分の判定は別途 hash を検討）

## raw を保存するか？
初期は **不要**（まずは normalized のみで進める）  
必要になったら、将来 `raw_json` を別テーブルに追加する。
