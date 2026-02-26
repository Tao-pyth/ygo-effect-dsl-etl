# 00_scope — 役割定義（Scope）

## ミッション（1行）
YGOPRODeck API からカード情報と画像を取得し、正規化して SQLite に格納し、研究用コーパスとして **全件を JSONL + manifest で出力**する。

## このリポジトリがやること（Included）
- API 取得（主：YGOPRODeck `cardinfo.php`、`misc=yes` を利用）
- 画像ダウンロード（保存先と相対パス管理）
- SQLite 正規化ストア（冪等な upsert）
- 全件エクスポート（`data/export/cards.jsonl` + `data/export/manifest.json`）
- 基本的な健全性確認（件数、必須項目欠損率など）

## このリポジトリがやらないこと（Explicitly Excluded）
- DSL 変換（効果の構造化、辞書、テンプレ抽出）
- 探索・分析（状態遷移探索、グラフ化、Neo4j投入等）
- 効果テキストの「意味解釈」

## 全体フロー
```text
API → (sync) → SQLite(normalized) → (export full) → cards.jsonl + manifest.json → CORE(ygo-effect-dsl)
```

## 重要な設計原則
- **研究ロジックはCOREへ**：ETLはデータ工学の領域に限定する
- **冪等性**：同じデータを何度取り込んでも壊れない
- **契約（Contract）**：COREとの受け渡しは JSONL+manifest を唯一の正とする
- **日本語の後追い取得を想定**：初期から DB/JSONL に `name_ja` / `card_text_ja` 等の「空欄」を持てるようにする
