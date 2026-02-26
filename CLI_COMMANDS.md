# CLI コマンド案（ygo-effect-dsl-etl）

このリポジトリは **ETL専用**（取得→SQLite格納→全件export）です。研究ロジック（DSL化/探索）は含めません。

---

## コマンド一覧（推奨：最小）

### 1) sync
**API取得 → 画像取得 → SQLite格納（冪等）**

```bash
python -m ygo_effect_dsl_etl sync
```

主なオプション案（必要になったら追加）
- `--db data/db/normalized.sqlite`
- `--images-dir data/images`
- `--lang en`（初期は en 固定でもOK）
- `--request-locale ja`（将来の日本語系で利用）
- `--rate-limit-ms 200`（レート制御）
- `--timeout 30`

### 2) export
**SQLite → 全件JSONL（data/export/ 固定） + manifest 生成**

```bash
python -m ygo_effect_dsl_etl export
```

主なオプション案
- `--db data/db/normalized.sqlite`
- `--out-dir data/export`（既定：data/export）
- `--with-images false`（原則：相対パスのみ。画像同梱は後回しでOK）

---

## 将来追加（枠だけ先に用意すると楽）

### enrich-ja
**日本語名・日本語効果文の後追い取得（別口ソース）→ SQLite 更新（冪等）**

```bash
python -m ygo_effect_dsl_etl enrich-ja
```

- 初期実装では「コマンドの器（入口と設定だけ）」を置いておき、実データ取得は後から差し替え可能にするのが安全です。

### doctor
**データ健全性（欠損率/件数/画像率）を集計**

```bash
python -m ygo_effect_dsl_etl doctor
```

---

## 期待する終了コード（運用向け）
- `0`：成功
- `1`：処理失敗（例外）
- `2`：入力/設定エラー（設定不足、パス不正など）

---

## ログ出力（推奨）
- `data/logs/etl_YYYYMMDD.log` のように日付単位で追記
- バッチからも確認しやすいように標準出力にも要点を出す
