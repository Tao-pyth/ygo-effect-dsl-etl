from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from ygo_effect_dsl_etl.config import EtlConfig
from ygo_effect_dsl_etl.db import get_connection, iter_cards

LOGGER = logging.getLogger(__name__)

FIELDS = [
    "export_schema_version",
    "cid",
    "name_en",
    "card_text_en",
    "name_ja",
    "card_text_ja",
    "card_info_en",
    "card_info_ja",
    "card_images_json",
    "image_url_full",
    "image_url_small",
    "image_url_cropped",
    "image_relpath_full",
    "image_relpath_small",
    "image_relpath_cropped",
    "fetched_at",
    "source",
]


def _empty(v: object) -> str:
    if v is None:
        return ""
    return str(v)


def run_export(config: EtlConfig) -> int:
    if not config.db_path.exists():
        LOGGER.error("database does not exist: %s", config.db_path)
        return 2

    conn = get_connection(config.db_path)
    rows = list(iter_cards(conn))
    conn.close()

    config.export_dir.mkdir(parents=True, exist_ok=True)
    cards_path = config.export_dir / "cards.jsonl"
    manifest_path = config.export_dir / "manifest.json"

    has_images = False
    with cards_path.open("w", encoding="utf-8") as f:
        for row in rows:
            rec = {
                "export_schema_version": config.export_schema_version,
                "cid": int(row["cid"]),
                "name_en": _empty(row["name_en"]),
                "card_text_en": _empty(row["card_text_en"]),
                "name_ja": _empty(row["name_ja"]),
                "card_text_ja": _empty(row["card_text_ja"]),
                "card_info_en": _empty(row["card_info_en"]),
                "card_info_ja": _empty(row["card_info_ja"]),
                "card_images_json": _empty(row["card_images_json"]),
                "image_url_full": _empty(row["image_url_full"]),
                "image_url_small": _empty(row["image_url_small"]),
                "image_url_cropped": _empty(row["image_url_cropped"]),
                "image_relpath_full": _empty(row["image_relpath_full"]),
                "image_relpath_small": _empty(row["image_relpath_small"]),
                "image_relpath_cropped": _empty(row["image_relpath_cropped"]),
                "fetched_at": _empty(row["fetched_at"]),
                "source": _empty(row["source"]),
            }
            has_images = has_images or any(
                bool(rec[key])
                for key in ("image_relpath_full", "image_relpath_small", "image_relpath_cropped")
            )
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    manifest = {
        "export_schema_version": config.export_schema_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(rows),
        "languages": ["en", "ja"],
        "has_images": has_images,
        "fields": FIELDS,
        "source": {
            "name": config.source_name,
            "endpoint": config.api_endpoint,
            "misc": "yes",
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    LOGGER.info("export complete: %s (%d records)", cards_path, len(rows))
    return 0
