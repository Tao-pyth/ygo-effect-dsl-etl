# ygo-effect-dsl-etl

YGOPRODeck API からカード情報を取得し、SQLiteへ正規化保存して、研究用コーパス（JSONL + manifest）を出力する **ETL専用** リポジトリです。

## Scope
- やること: `sync`（取得/保存）・`export`（全件出力）
- やらないこと: DSL化、探索・分析、意味解釈

詳細は docs を参照:
- [00_scope](docs/00_scope.md)
- [10_contract_export](docs/10_contract_export.md)
- [15_japanese_enrichment_plan](docs/15_japanese_enrichment_plan.md)
- [20_data_model_sqlite](docs/20_data_model_sqlite.md)
- [30_reproducibility](docs/30_reproducibility.md)
- [40_operations](docs/40_operations.md)
- [50_changelog_policy](docs/50_changelog_policy.md)
- [60_test_plan](docs/60_test_plan.md)

## CLI
```bash
python -m ygo_effect_dsl_etl sync
python -m ygo_effect_dsl_etl export
python -m ygo_effect_dsl_etl enrich-ja
python -m ygo_effect_dsl_etl doctor
```

終了コード:
- 0: 成功
- 1: 実行失敗
- 2: 設定エラー

## Export contract (minimum)
`data/export/cards.jsonl`:
- `export_schema_version`
- `cid` (konami_id)
- `name_en`, `card_text_en`
- `name_ja`, `card_text_ja`
- `card_info_en`, `card_info_ja`
- `image_relpath`
- `fetched_at`
- `source`

`data/export/manifest.json`:
- `export_schema_version`, `created_at`, `record_count`
- `languages`, `has_images`, `fields`, `source`

## Windows operation scripts
- `scripts/run_sync_export.bat`
- `scripts/run_sync_export.ps1`
