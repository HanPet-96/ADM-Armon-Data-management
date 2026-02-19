from __future__ import annotations

import argparse
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


def main() -> int:
    parser = argparse.ArgumentParser(description="Resize splash image with max bounds while keeping aspect ratio")
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("max_w", type=int)
    parser.add_argument("max_h", type=int)
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    img = QImage(str(src))
    if img.isNull():
        return 2

    if img.width() > args.max_w or img.height() > args.max_h:
        img = img.scaled(
            args.max_w,
            args.max_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not img.save(str(dst)):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

