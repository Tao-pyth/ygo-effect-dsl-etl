from __future__ import annotations

import argparse
import logging
from datetime import datetime

from ygo_effect_dsl_etl.config import DEFAULT_CONFIG, EtlConfig
from ygo_effect_dsl_etl.doctor import run_doctor
from ygo_effect_dsl_etl.enrich import run_enrich_ja
from ygo_effect_dsl_etl.export import run_export
from ygo_effect_dsl_etl.sync import run_sync


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ygo_effect_dsl_etl")
    sub = parser.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="Fetch API data and upsert into SQLite")
    sync.add_argument("--image-download-start-delay-sec", type=float, default=DEFAULT_CONFIG.image_download_start_delay_sec)
    sync.add_argument("--image-between-ms", type=int, default=DEFAULT_CONFIG.image_between_ms)
    sync.add_argument("--image-retry-count", type=int, default=DEFAULT_CONFIG.image_retry_count)
    sync.add_argument("--image-retry-backoff-sec", type=float, default=DEFAULT_CONFIG.image_retry_backoff_sec)
    sub.add_parser("export", help="Export SQLite data into JSONL + manifest")
    sub.add_parser("enrich-ja", help="Scaffold for Japanese backfill")
    sub.add_parser("doctor", help="Scaffold for ETL health checks")
    return parser


class _ContextDefaultsFilter(logging.Filter):
    def __init__(self, run_id: str, command: str) -> None:
        super().__init__()
        self.run_id = run_id
        self.command = command

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = getattr(record, "run_id", self.run_id)
        record.command = getattr(record, "command", self.command)
        record.cid = getattr(record, "cid", "")
        record.url = getattr(record, "url", "")
        record.attempt = getattr(record, "attempt", "")
        record.elapsed_ms = getattr(record, "elapsed_ms", "")
        return True


def configure_logging(command: str = "bootstrap", run_id: str | None = None) -> str:
    resolved_run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    DEFAULT_CONFIG.logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = DEFAULT_CONFIG.logs_dir / f"etl_{datetime.now().strftime('%Y%m%d')}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s run_id=%(run_id)s command=%(command)s "
        "cid=%(cid)s url=%(url)s attempt=%(attempt)s elapsed_ms=%(elapsed_ms)s - %(message)s"
    )
    context_filter = _ContextDefaultsFilter(run_id=resolved_run_id, command=command)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(context_filter)
    root_logger.addHandler(stream_handler)

    return resolved_run_id


def main(argv: list[str] | None = None) -> int:
    run_id = configure_logging()
    parser = _build_parser()
    args = parser.parse_args(argv)
    configure_logging(command=args.command, run_id=run_id)
    config: EtlConfig = DEFAULT_CONFIG

    try:
        if args.command == "sync":
            config = EtlConfig(
                **{
                    **DEFAULT_CONFIG.__dict__,
                    "image_download_start_delay_sec": args.image_download_start_delay_sec,
                    "image_between_ms": args.image_between_ms,
                    "image_retry_count": args.image_retry_count,
                    "image_retry_backoff_sec": args.image_retry_backoff_sec,
                }
            )
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
