from pathlib import Path

from adm_app.settings_store import AppSettings, load_settings, save_settings


def test_settings_store_roundtrip(tmp_path: Path):
    settings_path = tmp_path / "settings.json"
    default_root = tmp_path / "DatastructDefault"
    loaded = load_settings(default_data_root=default_root, settings_path=settings_path)
    assert loaded.data_root == str(default_root)

    save_settings(AppSettings(data_root=str(tmp_path / "DatastructNew")), settings_path=settings_path)
    reloaded = load_settings(default_data_root=default_root, settings_path=settings_path)
    assert reloaded.data_root == str(tmp_path / "DatastructNew")

