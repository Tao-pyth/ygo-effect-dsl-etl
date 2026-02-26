# ygo-effect-dsl-etl

## Overview

This repository generates a normalized card corpus for
**ygo-effect-dsl**.

Its responsibility is strictly limited to:

-   Fetching card data from API
-   Downloading card images
-   Normalizing and storing data into SQLite
-   Exporting the full dataset as JSONL + manifest

This repository **does not** contain any DSL logic, analysis, or
exploration code.

------------------------------------------------------------------------

## Mission

To provide a reproducible, normalized, machine-readable corpus of card
data that can be consumed by `ygo-effect-dsl` for state-transition
modeling and exploration.

------------------------------------------------------------------------

## Responsibilities

### Included

-   API ingestion (ja / en)
-   Image download and storage
-   SQLite normalization
-   Idempotent sync
-   Full corpus export
-   Basic health diagnostics

### Explicitly Excluded

-   DSL transformation
-   Effect parsing or interpretation
-   Exploration logic
-   Graph generation (Neo4j etc.)
-   Research-level semantics

------------------------------------------------------------------------

## Architecture

    API
    │
    ├─ sync → SQLite (normalized)
    │
    └─ export → cards.jsonl
               → manifest.json

------------------------------------------------------------------------

## Directory Structure

    data/
    ├── db/
    │   └── normalized.sqlite
    ├── images/
    │   └── <cid>.jpg
    └── export/
        ├── cards.jsonl
        └── manifest.json

------------------------------------------------------------------------

## CLI

### Sync (Fetch → Normalize → Store)

``` bash
python -m ygo_effect_dsl_etl sync
```

-   Fetch data from API
-   Download images
-   Upsert into SQLite
-   Safe to run multiple times (idempotent)

------------------------------------------------------------------------

### Export (Full Corpus)

``` bash
python -m ygo_effect_dsl_etl export
```

-   Exports all records to:
    -   data/export/cards.jsonl
    -   data/export/manifest.json

------------------------------------------------------------------------

## Export Contract

### cards.jsonl (1 record per line)

Minimum fields:

-   cid
-   name_ja
-   name_en
-   card_text_ja
-   card_text_en
-   card_info_ja
-   card_info_en
-   image_relpath
-   source
-   fetched_at
-   export_schema_version

------------------------------------------------------------------------

### manifest.json

Contains:

-   export_schema_version
-   created_at
-   record_count
-   languages
-   has_images
-   fields
-   source

------------------------------------------------------------------------

## Reproducibility

The exported JSONL file is the canonical dataset used by:

ygo-effect-dsl

The DSL repository must not depend on the internal SQLite structure.

------------------------------------------------------------------------

## Design Principles

-   Clear separation between data engineering and research logic
-   Idempotent execution
-   Schema versioning for forward compatibility
-   No semantic interpretation of effect text

------------------------------------------------------------------------

## Future Scope (Optional)

-   Data health diagnostics (`doctor` command)
-   Export compression (zstd)
-   Parallel fetch improvements

------------------------------------------------------------------------

## License

TBD
