from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from ygo_effect_dsl_etl.config import EtlConfig
from ygo_effect_dsl_etl.db import ensure_schema, get_connection, upsert_card

LOGGER = logging.getLogger(__name__)


def _fetch_card_data(endpoint: str, timeout_s: int) -> list[dict]:
    req = Request(endpoint, headers={"User-Agent": "ygo-effect-dsl-etl/0.1"})
    with urlopen(req, timeout=timeout_s) as res:
        payload = json.loads(res.read().decode("utf-8"))
    return payload.get("data", [])


def _download_image(url: str, output_path: Path, timeout_s: int) -> bool:
    if not url:
        return False
    if output_path.exists() and output_path.stat().st_size > 0:
        return True
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = Request(url, headers={"User-Agent": "ygo-effect-dsl-etl/0.1"})
        with urlopen(req, timeout=timeout_s) as res:
            output_path.write_bytes(res.read())
        return True
    except URLError as exc:
        LOGGER.warning("image download failed: %s (%s)", url, exc)
        return False


def run_sync(config: EtlConfig) -> int:
    schema_path = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    try:
        cards = _fetch_card_data(config.api_endpoint, config.request_timeout_s)
    except Exception as exc:
        LOGGER.exception("failed to fetch API payload: %s", exc)
        return 1

    conn = get_connection(config.db_path)
    ensure_schema(conn, schema_path)

    fetched_at = datetime.now(timezone.utc).isoformat()
    inserted = 0
    skipped_missing_konami = 0

    for card in cards:
        cid = card.get("misc_info", [{}])[0].get("konami_id")
        if not cid:
            skipped_missing_konami += 1
            LOGGER.info("skip card without konami_id: ygoprodeck_id=%s", card.get("id", ""))
            continue

        image_url = ""
        images = card.get("card_images") or []
        if images:
            image_url = images[0].get("image_url", "") or ""

        image_relpath = ""
        if image_url:
            image_path = config.images_dir / f"{cid}.jpg"
            if _download_image(image_url, image_path, config.request_timeout_s):
                image_relpath = str(image_path.as_posix())

        record = {
            "cid": int(cid),
            "name_en": card.get("name", "") or "",
            "card_text_en": card.get("desc", "") or "",
            "name_ja": "",
            "card_text_ja": "",
            "card_info_en": json.dumps(card, ensure_ascii=False, sort_keys=True),
            "card_info_ja": "",
            "image_relpath": image_relpath,
            "fetched_at": fetched_at,
            "source": config.source_name,
        }
        upsert_card(conn, record)
        inserted += 1

    conn.commit()
    conn.close()

    LOGGER.info("sync complete: upserted=%d skipped_no_konami_id=%d", inserted, skipped_missing_konami)
    return 0
