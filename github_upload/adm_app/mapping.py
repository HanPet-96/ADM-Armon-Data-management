from __future__ import annotations

import re
from typing import Iterable


CANONICAL_FIELDS = {
    "part_number": {"partno", "partnumber", "pn", "itemcode", "onderdeelnummer", "artikel"},
    "description": {"description", "desc", "omschrijving"},
    "qty": {"qty", "quantity", "aantal", "stuks"},
    "revision": {"rev", "revision", "versie"},
    "material": {"material", "materiaal"},
    "finish": {"finish", "afwerking"},
    "line_type": {"type", "parttype", "componenttype"},
    "status": {"status", "approvalstatus", "state"},
    "unit": {"uom", "unit", "eenheid"},
    "line_no": {"item", "itemno", "line", "regel", "pos", "position"},
}


def normalize_header(value: str) -> str:
    value = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", value)


def map_headers(headers: Iterable[object]) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for idx, raw in enumerate(headers):
        norm = normalize_header(str(raw))
        if not norm:
            continue
        for canonical, synonyms in CANONICAL_FIELDS.items():
            if norm == canonical or norm in synonyms:
                mapping[idx] = canonical
                break
    return mapping


def parse_qty(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None
