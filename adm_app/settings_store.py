from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppSettings:
    data_root: str
    theme_mode: str = "light"
    has_seen_help: bool = False
    language: str = "en"
    developer_mode: bool = False
    auto_reindex_on_startup: bool = True
    bom_default_expand_all: bool = False
    search_in_children: bool = True
    order_export_path: str = ""
    pdf_preview_engine: str = "web"


def app_data_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "ADM"
    return Path.home() / ".adm"


def default_settings_path() -> Path:
    return app_data_dir() / "settings.json"


def default_db_path() -> Path:
    return app_data_dir() / "adm.db"


def default_log_dir() -> Path:
    return app_data_dir() / "logs"


def default_order_export_path() -> Path:
    return Path.home() / "Documents" / "ADM-Export"


def load_settings(default_data_root: Path, settings_path: Path | None = None) -> AppSettings:
    path = settings_path or default_settings_path()
    if not path.exists():
        return AppSettings(
            data_root=str(default_data_root),
            order_export_path=str(default_order_export_path()),
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        data_root = str(payload.get("data_root", str(default_data_root)))
        theme_mode = str(payload.get("theme_mode", "light")).lower()
        if theme_mode not in {"light", "dark"}:
            theme_mode = "light"
        has_seen_help = bool(payload.get("has_seen_help", False))
        language = str(payload.get("language", "en")).lower()
        if language not in {"en", "nl"}:
            language = "en"
        developer_mode = bool(payload.get("developer_mode", False))
        auto_reindex_on_startup = bool(payload.get("auto_reindex_on_startup", True))
        bom_default_expand_all = bool(payload.get("bom_default_expand_all", False))
        search_in_children = bool(payload.get("search_in_children", True))
        raw_export_path = str(payload.get("order_export_path", "") or "").strip()
        order_export_path = raw_export_path or str(default_order_export_path())
        pdf_preview_engine = str(payload.get("pdf_preview_engine", "web")).lower().strip()
        if pdf_preview_engine not in {"web", "qtpdf"}:
            pdf_preview_engine = "web"
        return AppSettings(
            data_root=data_root,
            theme_mode=theme_mode,
            has_seen_help=has_seen_help,
            language=language,
            developer_mode=developer_mode,
            auto_reindex_on_startup=auto_reindex_on_startup,
            bom_default_expand_all=bom_default_expand_all,
            search_in_children=search_in_children,
            order_export_path=order_export_path,
            pdf_preview_engine=pdf_preview_engine,
        )
    except Exception:
        return AppSettings(
            data_root=str(default_data_root),
            theme_mode="light",
            has_seen_help=False,
            language="en",
            developer_mode=False,
            auto_reindex_on_startup=True,
            bom_default_expand_all=False,
            search_in_children=True,
            order_export_path=str(default_order_export_path()),
            pdf_preview_engine="web",
        )


def save_settings(settings: AppSettings, settings_path: Path | None = None) -> None:
    path = settings_path or default_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    theme_mode = settings.theme_mode if settings.theme_mode in {"light", "dark"} else "light"
    language = settings.language if settings.language in {"en", "nl"} else "en"
    pdf_preview_engine = settings.pdf_preview_engine if settings.pdf_preview_engine in {"web", "qtpdf"} else "web"
    payload = {
        "data_root": settings.data_root,
        "theme_mode": theme_mode,
        "has_seen_help": bool(settings.has_seen_help),
        "language": language,
        "developer_mode": bool(settings.developer_mode),
        "auto_reindex_on_startup": bool(settings.auto_reindex_on_startup),
        "bom_default_expand_all": bool(settings.bom_default_expand_all),
        "search_in_children": bool(settings.search_in_children),
        "order_export_path": str(settings.order_export_path or ""),
        "pdf_preview_engine": pdf_preview_engine,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
