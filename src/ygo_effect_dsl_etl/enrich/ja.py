from __future__ import annotations

import logging

from ygo_effect_dsl_etl.config import EtlConfig

LOGGER = logging.getLogger(__name__)


def run_enrich_ja(config: EtlConfig) -> int:
    LOGGER.info(
        "enrich-ja is a scaffold command for future JA backfill. db=%s",
        config.db_path,
    )
    return 0
