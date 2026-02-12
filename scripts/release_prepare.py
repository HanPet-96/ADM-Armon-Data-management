from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")


def validate_version(version: str) -> str:
    if not VERSION_RE.match(version):
        raise ValueError("Version must be in format MAJOR.MINOR.PATCH.BUILD (example: 1.0.0.1)")
    return version


def update_init_version(init_file: Path, version: str) -> None:
    text = init_file.read_text(encoding="utf-8")
    new_text, count = re.subn(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{version}"',
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Could not find __version__ assignment in {init_file}")
    init_file.write_text(new_text, encoding="utf-8")


def write_version_json(version_file: Path, version: str) -> None:
    version_file.write_text(json.dumps({"version": version}, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare ADM release version files")
    parser.add_argument("--version", required=True, help="Target version (MAJOR.MINOR.PATCH.BUILD)")
    args = parser.parse_args()

    version = validate_version(args.version)
    root = Path(__file__).resolve().parent.parent

    update_init_version(root / "adm_app" / "__init__.py", version)
    write_version_json(root / "version.json", version)

    print(f"[OK] Release version prepared: {version}")
    print("Updated:")
    print(" - adm_app/__init__.py")
    print(" - version.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
