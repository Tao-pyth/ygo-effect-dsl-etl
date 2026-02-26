from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


CARDS_REQUIRED_COLUMNS: dict[str, str] = {
    "card_images_json": "TEXT NOT NULL DEFAULT ''",
    "image_url_full": "TEXT NOT NULL DEFAULT ''",
    "image_url_small": "TEXT NOT NULL DEFAULT ''",
    "image_url_cropped": "TEXT NOT NULL DEFAULT ''",
    "image_relpath_full": "TEXT NOT NULL DEFAULT ''",
    "image_relpath_small": "TEXT NOT NULL DEFAULT ''",
    "image_relpath_cropped": "TEXT NOT NULL DEFAULT ''",
}


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    existing = {
        row[1]
        for row in conn.execute("PRAGMA table_info(cards)")
    }
    for name, ddl in CARDS_REQUIRED_COLUMNS.items():
        if name in existing:
            continue
        conn.execute(f"ALTER TABLE cards ADD COLUMN {name} {ddl}")
    conn.commit()


def upsert_card(conn: sqlite3.Connection, record: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO cards (
            cid, name_en, card_text_en, name_ja, card_text_ja,
            card_info_en, card_info_ja, card_images_json,
            image_url_full, image_url_small, image_url_cropped,
            image_relpath_full, image_relpath_small, image_relpath_cropped,
            fetched_at, source
        ) VALUES (
            :cid, :name_en, :card_text_en, :name_ja, :card_text_ja,
            :card_info_en, :card_info_ja, :card_images_json,
            :image_url_full, :image_url_small, :image_url_cropped,
            :image_relpath_full, :image_relpath_small, :image_relpath_cropped,
            :fetched_at, :source
        )
        ON CONFLICT(cid) DO UPDATE SET
            name_en=excluded.name_en,
            card_text_en=excluded.card_text_en,
            card_info_en=excluded.card_info_en,
            card_images_json=excluded.card_images_json,
            image_url_full=excluded.image_url_full,
            image_url_small=excluded.image_url_small,
            image_url_cropped=excluded.image_url_cropped,
            image_relpath_full=excluded.image_relpath_full,
            image_relpath_small=excluded.image_relpath_small,
            image_relpath_cropped=excluded.image_relpath_cropped,
            fetched_at=excluded.fetched_at,
            source=excluded.source
        """,
        record,
    )


def iter_cards(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute("SELECT * FROM cards ORDER BY cid ASC")
