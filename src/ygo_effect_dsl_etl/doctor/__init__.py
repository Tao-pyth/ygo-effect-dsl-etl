from __future__ import annotations

import logging

from ygo_effect_dsl_etl.config import EtlConfig

LOGGER = logging.getLogger(__name__)


def run_doctor(config: EtlConfig) -> int:
    LOGGER.info("doctor command scaffold. target db=%s", config.db_path)
    return 0
