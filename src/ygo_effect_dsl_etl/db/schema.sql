CREATE TABLE IF NOT EXISTS cards (
    cid INTEGER PRIMARY KEY,
    name_en TEXT NOT NULL DEFAULT '',
    card_text_en TEXT NOT NULL DEFAULT '',
    name_ja TEXT NOT NULL DEFAULT '',
    card_text_ja TEXT NOT NULL DEFAULT '',
    card_info_en TEXT NOT NULL DEFAULT '',
    card_info_ja TEXT NOT NULL DEFAULT '',
    image_relpath TEXT NOT NULL DEFAULT '',
    fetched_at TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'ygoprodeck'
);

CREATE INDEX IF NOT EXISTS idx_cards_source ON cards(source);
