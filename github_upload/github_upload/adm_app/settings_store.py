from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppSettings:
    data_root: str


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


def load_settings(default_data_root: Path, settings_path: Path | None = None) -> AppSettings:
    path = settings_path or default_settings_path()
    if not path.exists():
        return AppSettings(data_root=str(default_data_root))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        data_root = str(payload.get("data_root", str(default_data_root)))
        return AppSettings(data_root=data_root)
    except Exception:
        return AppSettings(data_root=str(default_data_root))


def save_settings(settings: AppSettings, settings_path: Path | None = None) -> None:
    path = settings_path or default_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"data_root": settings.data_root}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
