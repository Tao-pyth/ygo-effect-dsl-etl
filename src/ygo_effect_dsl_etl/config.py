from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EtlConfig:
    db_path: Path = Path("data/db/normalized.sqlite")
    images_dir: Path = Path("data/images")
    export_dir: Path = Path("data/export")
    logs_dir: Path = Path("data/logs")
    api_endpoint: str = "https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes"
    source_name: str = "ygoprodeck"
    export_schema_version: int = 1
    request_timeout_s: int = 30


DEFAULT_CONFIG = EtlConfig()
