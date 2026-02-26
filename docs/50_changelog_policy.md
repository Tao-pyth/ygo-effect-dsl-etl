# 50_changelog_policy — 変更履歴と互換性ポリシー

## 目的
ETLの変更が CORE を壊さないために、変更ルールを明文化する。

## 変更の種類
### 1) エクスポート契約（cards.jsonl / manifest.json）
- **破壊的変更**：必須キーの削除、名称変更、意味変更
  - `export_schema_version` をインクリメント
  - CHANGELOG に明記
- **非破壊変更**：任意キーの追加
  - `export_schema_version` は据え置き（推奨）
  - `manifest.json` の `fields` は更新

### 2) SQLite内部
- COREは依存しないため、内部変更は自由
- ただし `export` が出力する契約が変わる場合は上記に従う

## CHANGELOG運用（推奨）
- `CHANGELOG.md` を Keep a Changelog 形式で運用（任意）
- 重要なのは「COREに影響する変更」を見逃さないこと

## リリース方針（最小）
- `0.y.z` の間は破壊的変更が起こり得る
- `1.0.0` を切るときは export契約を安定させる
