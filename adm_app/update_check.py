from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any


DEFAULT_GITHUB_REPO = "HanPet-96/ADM-Armon-Data-management"


def normalize_version(value: str) -> tuple[int, ...]:
    text = (value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    text = text.split("-", 1)[0]
    parts = re.findall(r"\d+", text)
    if not parts:
        return (0,)
    return tuple(int(p) for p in parts)


def is_newer_version(current_version: str, candidate_version: str) -> bool:
    current = list(normalize_version(current_version))
    candidate = list(normalize_version(candidate_version))
    max_len = max(len(current), len(candidate))
    current += [0] * (max_len - len(current))
    candidate += [0] * (max_len - len(candidate))
    return tuple(candidate) > tuple(current)


def get_update_repo() -> str:
    return os.getenv("ADM_UPDATE_REPO", DEFAULT_GITHUB_REPO).strip()


def fetch_latest_github_release(timeout_seconds: float = 2.5) -> dict[str, Any] | None:
    repo = get_update_repo()
    if not repo:
        return None
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ADM-Armon-Data-management",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    tag = str(payload.get("tag_name") or "").strip()
    html_url = str(payload.get("html_url") or "").strip()
    if not tag:
        return None
    return {
        "tag_name": tag,
        "html_url": html_url,
    }
