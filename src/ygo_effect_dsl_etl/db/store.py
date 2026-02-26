from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()


def upsert_card(conn: sqlite3.Connection, record: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO cards (
            cid, name_en, card_text_en, name_ja, card_text_ja,
            card_info_en, card_info_ja, image_relpath, fetched_at, source
        ) VALUES (
            :cid, :name_en, :card_text_en, :name_ja, :card_text_ja,
            :card_info_en, :card_info_ja, :image_relpath, :fetched_at, :source
        )
        ON CONFLICT(cid) DO UPDATE SET
            name_en=excluded.name_en,
            card_text_en=excluded.card_text_en,
            card_info_en=excluded.card_info_en,
            image_relpath=excluded.image_relpath,
            fetched_at=excluded.fetched_at,
            source=excluded.source
        """,
        record,
    )


def iter_cards(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute("SELECT * FROM cards ORDER BY cid ASC")
