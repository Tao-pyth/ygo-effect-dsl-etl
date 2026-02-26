from __future__ import annotations

import argparse
import logging

from ygo_effect_dsl_etl.config import DEFAULT_CONFIG, EtlConfig
from ygo_effect_dsl_etl.doctor import run_doctor
from ygo_effect_dsl_etl.enrich import run_enrich_ja
from ygo_effect_dsl_etl.export import run_export
from ygo_effect_dsl_etl.sync import run_sync


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ygo_effect_dsl_etl")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sync", help="Fetch API data and upsert into SQLite")
    sub.add_parser("export", help="Export SQLite data into JSONL + manifest")
    sub.add_parser("enrich-ja", help="Scaffold for Japanese backfill")
    sub.add_parser("doctor", help="Scaffold for ETL health checks")
    return parser


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    parser = _build_parser()
    args = parser.parse_args(argv)
    config: EtlConfig = DEFAULT_CONFIG

    try:
        if args.command == "sync":
            return run_sync(config)
        if args.command == "export":
            return run_export(config)
        if args.command == "enrich-ja":
            return run_enrich_ja(config)
        if args.command == "doctor":
            return run_doctor(config)
        return 2
    except ValueError as exc:
        logging.getLogger(__name__).error("configuration error: %s", exc)
        return 2
    except Exception:
        logging.getLogger(__name__).exception("command failed")
        return 1
