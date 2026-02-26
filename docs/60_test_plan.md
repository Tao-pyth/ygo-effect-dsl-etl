# 60_test_plan — テスト計画（最小）

## 目的
ETLの最重要成果物（cards.jsonl + manifest.json）が常に正しい形で出力されることを保証する。

## 最小テスト（自動化しやすい）
### A. Export スキーマ検査
- `manifest.json` の必須キーが存在する
- `cards.jsonl` の先頭N件（例：100件）で必須キーが存在する
- `export_schema_version` が全件で同一
- `cid` が空でない

### B. 件数整合
- `manifest.record_count` == `cards.jsonl` の行数

### C. 文字列の扱い
- UTF-8 で読める
- 改行を含むカードテキストでも JSONL が壊れない（JSONエスケープが正しい）

### D. 画像パス（任意）
- `image_relpath` が空でない場合、実ファイルが存在する（サンプル件数でOK）

## 手動テスト（最初だけでもOK）
- `sync` を1回実行し、SQLiteに最低1件入ること
- `export` で `data/export/` にファイルが生成されること
- 失敗させても再実行で復旧すること（冪等性）

## CIに乗せる場合（将来）
- small fixture DB を用意し、ネットワーク無しで `export` をテストする
