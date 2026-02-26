# 10_contract_export — エクスポート契約（ETL → CORE）

このドキュメントは、ETL が出力するデータセットを CORE（ygo-effect-dsl）が取り込むための **契約**を定義します。

## 出力先（固定）
- `data/export/cards.jsonl`
- `data/export/manifest.json`

## スキーマバージョン
- `export_schema_version`: 整数
- 破壊的変更（必須キーの削除・名称変更・意味変更）が入る場合にインクリメントする

---

## cards.jsonl（全件、1行=1カード）

### 1レコードの基本方針
- 文字コード：UTF-8
- 改行：LF（推奨）
- 欠損：**空文字**（原則）  
  - API側が null / キー欠落の場合でも、ETL は出力を安定させるため **キーを出し、空文字**に寄せる

### 主キー（cid）
- `cid` は **Konami ID（`konami_id`）** を採用する
- `cid` は JSONL では `int` もしくは `str` でよいが、全レコードで統一する（推奨：`int`）

> 注：YGOPRODeck の `id`（パスコード）ではなく、`konami_id` をキーにする（APIガイド参照）。

### フィールド仕様（最小必須）

| key | required | type | 例 | 備考 |
|---|---:|---|---|---|
| export_schema_version | yes | int | 2 | |
| cid | yes | int | 123456 | Konami ID |
| name_en | yes | str | "Dark Magician" | APIの `name` |
| card_text_en | yes | str | "..." | APIの `desc` |
| name_ja | yes | str | "ブラック・マジシャン" | 初期は空でもOK（後追い取得） |
| card_text_ja | yes | str | "..." | 初期は空でもOK（後追い取得） |
| card_info_en | yes | object/str | {...} | type/atk/def 等。構造は自由だが安定させる |
| card_info_ja | yes | object/str | {...} | 初期は空でもOK（後追い取得） |
| card_images_json | yes | str | "[{...}]" | API `card_images` 配列をlossless保持 |
| image_url_full | yes | str | "https://..." | `card_images[0].image_url` |
| image_url_small | yes | str | "https://..." | `card_images[0].image_url_small` |
| image_url_cropped | yes | str | "https://..." | `card_images[0].image_url_cropped` |
| image_relpath_full | yes | str | "data/images/123456_full.jpg" | 無ければ空文字 |
| image_relpath_small | yes | str | "data/images/123456_small.jpg" | 無ければ空文字 |
| image_relpath_cropped | yes | str | "data/images/123456_cropped.jpg" | 無ければ空文字 |
| fetched_at | yes | str | "2026-02-26T12:34:56+09:00" | ISO8601 |
| source | yes | str | "ygoprodeck" | |

### 画像3種の扱い
- YGOPRODeck API の `card_images` 配列から `image_url` / `image_url_small` / `image_url_cropped` を取得する。
- 代替イラスト対応のため、配列全体を `card_images_json` に保存する。
- primary画像は `card_images[0]` を使用する。
- ETLは URL確定後の猶予時間を置いて画像DLを開始し、失敗時は relpath を空文字にして継続する。

### misc=yes の取り扱い
- ETL は `misc=yes` を有効にし、返ってきた追加情報を **失わない**形で保持する（`card_info_en` 内に保持可）
- `konami_id` が返る場合は **必ず cid として採用**する

---

## manifest.json（目次）

### 必須フィールド
- `export_schema_version`（int）
- `created_at`（ISO8601）
- `record_count`（int）
- `languages`（例：`["en","ja"]`）
- `has_images`（bool）
- `fields`（配列：cards.jsonl のキー一覧）
- `source`（例：`{"name":"ygoprodeck","endpoint":"cardinfo.php","misc":"yes"}`）

### 推奨フィールド（任意）
- `notes`（自由記述）
- `db_version`（YGOPRODeck の checkDBVer を使う場合）
