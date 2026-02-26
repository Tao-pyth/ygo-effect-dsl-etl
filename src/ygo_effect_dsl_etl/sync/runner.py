from __future__ import annotations

import json
import logging
import time
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


def _download_image(url: str, output_path: Path, timeout_s: int, retry_count: int, retry_backoff_sec: float) -> bool:
    if not url:
        return False
    if output_path.exists() and output_path.stat().st_size > 0:
        return True
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retry_count + 1):
        try:
            req = Request(url, headers={"User-Agent": "ygo-effect-dsl-etl/0.1"})
            with urlopen(req, timeout=timeout_s) as res:
                output_path.write_bytes(res.read())
            return True
        except URLError as exc:
            if attempt >= retry_count:
                LOGGER.warning("image download failed after retries: %s (%s)", url, exc)
                return False
            backoff = retry_backoff_sec * (2 ** (attempt - 1))
            LOGGER.info("image download retry: url=%s attempt=%d/%d backoff=%.2fs", url, attempt, retry_count, backoff)
            time.sleep(backoff)
    return False


def _to_relpath(path: Path) -> str:
    return str(path.as_posix())


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

    pending_images: list[tuple[int, dict[str, str]]] = []

    for card in cards:
        cid = card.get("misc_info", [{}])[0].get("konami_id")
        if not cid:
            skipped_missing_konami += 1
            LOGGER.info("skip card without konami_id: ygoprodeck_id=%s", card.get("id", ""))
            continue

        images = card.get("card_images") or []
        primary_image = images[0] if images else {}
        image_url_full = primary_image.get("image_url", "") or ""
        image_url_small = primary_image.get("image_url_small", "") or ""
        image_url_cropped = primary_image.get("image_url_cropped", "") or ""

        image_full_path = config.images_dir / f"{cid}_full.jpg"
        image_small_path = config.images_dir / f"{cid}_small.jpg"
        image_cropped_path = config.images_dir / f"{cid}_cropped.jpg"

        image_relpath_full = _to_relpath(image_full_path) if image_url_full else ""
        image_relpath_small = _to_relpath(image_small_path) if image_url_small else ""
        image_relpath_cropped = _to_relpath(image_cropped_path) if image_url_cropped else ""

        record = {
            "cid": int(cid),
            "name_en": card.get("name", "") or "",
            "card_text_en": card.get("desc", "") or "",
            "name_ja": "",
            "card_text_ja": "",
            "card_info_en": json.dumps(card, ensure_ascii=False, sort_keys=True),
            "card_info_ja": "",
            "card_images_json": json.dumps(images, ensure_ascii=False, sort_keys=True),
            "image_url_full": image_url_full,
            "image_url_small": image_url_small,
            "image_url_cropped": image_url_cropped,
            "image_relpath_full": image_relpath_full,
            "image_relpath_small": image_relpath_small,
            "image_relpath_cropped": image_relpath_cropped,
            "fetched_at": fetched_at,
            "source": config.source_name,
        }
        upsert_card(conn, record)
        pending_images.append(
            (
                int(cid),
                {
                    "image_url_full": image_url_full,
                    "image_url_small": image_url_small,
                    "image_url_cropped": image_url_cropped,
                    "image_relpath_full": image_relpath_full,
                    "image_relpath_small": image_relpath_small,
                    "image_relpath_cropped": image_relpath_cropped,
                },
            )
        )
        inserted += 1

    conn.commit()

    if pending_images and config.image_download_start_delay_sec > 0:
        LOGGER.info("waiting %.2fs before image downloads", config.image_download_start_delay_sec)
        time.sleep(config.image_download_start_delay_sec)

    download_attempted = 0
    download_success = 0
    for cid, image_info in pending_images:
        for url_key, relpath_key in (
            ("image_url_full", "image_relpath_full"),
            ("image_url_small", "image_relpath_small"),
            ("image_url_cropped", "image_relpath_cropped"),
        ):
            image_url = image_info[url_key]
            image_relpath = image_info[relpath_key]
            if not image_url:
                continue
            output_path = Path(image_relpath)
            download_attempted += 1
            ok = _download_image(
                image_url,
                output_path,
                config.request_timeout_s,
                config.image_retry_count,
                config.image_retry_backoff_sec,
            )
            if ok:
                download_success += 1
            else:
                conn.execute(
                    f"UPDATE cards SET {relpath_key}='' WHERE cid=?",
                    (cid,),
                )

            if config.image_between_ms > 0:
                time.sleep(config.image_between_ms / 1000)

    conn.commit()
    conn.close()

    LOGGER.info(
        "sync complete: upserted=%d skipped_no_konami_id=%d image_downloads=%d/%d",
        inserted,
        skipped_missing_konami,
        download_success,
        download_attempted,
    )
    return 0
