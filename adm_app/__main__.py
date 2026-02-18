from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .db import get_connection, init_db
from .indexer import run_index
from .settings_store import (
    AppSettings,
    default_db_path,
    default_log_dir,
    load_settings,
    save_settings,
)
from .ui import run_ui
from . import __version__


def default_data_root() -> Path:
    return (Path(__file__).resolve().parent.parent / ".." / "Datastruct").resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ADM - Armon Data Management")
    parser.add_argument("--version", action="version", version=f"ADM {__version__}")
    parser.add_argument("--data-root", default=None, help="Path to Datastruct")
    parser.add_argument("--db-path", default=None, help="SQLite database path")
    parser.add_argument("--reindex", action="store_true", help="Run index before starting UI")
    parser.add_argument("--no-ui", action="store_true", help="Only run CLI actions and exit")
    return parser.parse_args()


def configure_logging() -> None:
    log_dir = default_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "adm.log", encoding="utf-8"),
        ],
    )


def main() -> int:
    configure_logging()
    args = parse_args()
    defaults_root = default_data_root()
    settings = load_settings(default_data_root=defaults_root)
    data_root = Path(args.data_root).resolve() if args.data_root else Path(settings.data_root).resolve()
    if args.data_root:
        save_settings(
            AppSettings(
                data_root=str(data_root),
                theme_mode=settings.theme_mode,
                has_seen_help=settings.has_seen_help,
                language=settings.language,
                developer_mode=settings.developer_mode,
            )
        )
    db_path = Path(args.db_path).resolve() if args.db_path else default_db_path()
    conn = get_connection(db_path)
    init_db(conn)
    if args.reindex and args.no_ui:
        stats = run_index(conn, data_root)
        print(
            f"Indexed: boms={stats.boms_parsed}, lines={stats.lines_imported}, "
            f"warnings={stats.warnings_count}, errors={stats.errors_count}"
        )
    if args.no_ui:
        return 0
    return run_ui(
        conn,
        data_root=str(data_root),
        theme_mode=settings.theme_mode,
        has_seen_help=settings.has_seen_help,
        language=settings.language,
        developer_mode=settings.developer_mode,
    )


if __name__ == "__main__":
    raise SystemExit(main())
