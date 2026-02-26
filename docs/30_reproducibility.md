# 30_reproducibility — 再現性（Reproducibility）

## 目的
誰が実行しても同じ形式のコーパス（cards.jsonl + manifest.json）を生成できるようにする。

## 最小手順
1. `sync`：取得→SQLite格納
2. `export`：SQLite→全件JSONL出力

## 出力が変わる要因
- API側データ更新（新カード追加・既存更新）
- `misc=yes` の追加項目の変化
- 画像取得の成否（ネットワーク/404）

## 再現性を上げるための運用
- `manifest.json` に `created_at` / `record_count` / `fields` を必ず出す
- 可能なら API の DB バージョン（checkDBVer）を記録する（任意）
- `export_schema_version` を上げる条件を `docs/10_contract_export.md` と一致させる

## 研究用 mini corpus（将来）
- `export --limit N` や `export --ids ...` のような機能で、COREが同梱可能な小規模データを作れると便利
- 初期実装では不要（全件 export のみでOK）
