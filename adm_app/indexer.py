from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3

from .db import (
    clear_article_lines_for_run,
    finish_import_run,
    log_issue,
    start_import_run,
    upsert_article,
    upsert_document,
    upsert_part,
    insert_bom_line,
)
from .excel_parser import parse_bom_file


PART_REGEX = re.compile(r"\b([A-Z]{0,4}\d{3,}[A-Z0-9\-]*)\b", re.IGNORECASE)
DOC_PART_PATTERN = re.compile(r"(?<!\d)(\d{2}-\d{5,6})(?!\d)", re.IGNORECASE)
TOKEN_SPLIT_REGEX = re.compile(r"[^A-Z0-9]+")
COMMON_TOKENS = {
    "THE",
    "AND",
    "FOR",
    "WITH",
    "MANUAL",
    "DOC",
    "DOCUMENT",
    "EN",
    "NL",
    "DE",
    "FR",
    "REV",
    "V",
}
DOC_EXT_TO_TYPE = {
    ".pdf": "pdf",
    ".step": "step",
    ".stp": "step",
    ".dwg": "dwg",
    ".dxf": "dwg",
}


@dataclass
class IndexStats:
    files_scanned: int = 0
    boms_parsed: int = 0
    lines_imported: int = 0
    warnings_count: int = 0
    errors_count: int = 0


def run_index(conn: sqlite3.Connection, data_root: Path, force_doc_relink: bool = False) -> IndexStats:
    stats = IndexStats()
    run_id = start_import_run(conn)
    try:
        boms_path = data_root / "BOMS"
        boms_changed = False
        existing_by_path: dict[str, sqlite3.Row] = {}
        for row in conn.execute(
            "SELECT id, source_bom_path, source_bom_modified_at, source_bom_size_bytes FROM articles"
        ).fetchall():
            source_path = str(row["source_bom_path"] or "").strip()
            if source_path:
                existing_by_path[source_path.casefold()] = row
        bom_files = sorted(
            [*boms_path.rglob("*.xlsx"), *boms_path.rglob("*.xls"), *boms_path.rglob("*.xlsm")]
        )
        stats.files_scanned += len(bom_files)
        for bom_file in bom_files:
            try:
                stat = bom_file.stat()
                modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="microseconds")
                size_bytes = int(stat.st_size)
                existing = existing_by_path.get(str(bom_file.resolve()).casefold())
                if (
                    existing is not None
                    and str(existing["source_bom_modified_at"] or "") == modified_at
                    and int(existing["source_bom_size_bytes"] or 0) == size_bytes
                ):
                    continue
                parsed = parse_bom_file(bom_file)
                article_id = upsert_article(
                    conn,
                    article_number=parsed.article_number,
                    title=parsed.article_title,
                    source_bom_path=str(parsed.source_file),
                    source_bom_filename=parsed.source_file.name,
                    source_bom_modified_at=modified_at,
                    source_bom_size_bytes=size_bytes,
                )
                boms_changed = True
                clear_article_lines_for_run(conn, article_id)
                for line in parsed.lines:
                    if not line.part_number:
                        stats.warnings_count += 1
                        log_issue(
                            conn,
                            run_id=run_id,
                            severity="warning",
                            message="Skipped BOM row without part number",
                            file_path=str(bom_file),
                            sheet_name=line.source_sheet,
                            row_number=line.source_row_number,
                        )
                        continue
                    part_id = upsert_part(conn, line.part_number.upper(), line.description)
                    insert_bom_line(
                        conn=conn,
                        article_id=article_id,
                        part_id=part_id,
                        item_no=line.item_no,
                        line_no=line.line_no,
                        qty=line.qty,
                        unit=line.unit,
                        revision=line.revision,
                        description=line.description,
                        material=line.material,
                        finish=line.finish,
                        line_type=line.line_type,
                        status=line.status,
                        raw_columns=line.raw_columns,
                        source_sheet=line.source_sheet,
                        source_row_number=line.source_row_number,
                        run_id=run_id,
                    )
                    stats.lines_imported += 1
                stats.boms_parsed += 1
                conn.commit()
            except Exception as exc:
                stats.errors_count += 1
                log_issue(
                    conn,
                    run_id=run_id,
                    severity="error",
                    message=f"Failed to parse BOM: {exc}",
                    file_path=str(bom_file),
                )
                conn.commit()
        removed_articles = remove_missing_articles(conn, boms_root=boms_path.resolve())
        should_force_doc_relink = force_doc_relink or boms_changed or removed_articles > 0
        index_documents(conn, data_root, run_id, force_relink=should_force_doc_relink)
        status = "completed_with_warnings" if stats.warnings_count or stats.errors_count else "completed"
        finish_import_run(
            conn,
            run_id,
            status=status,
            files_scanned=stats.files_scanned,
            boms_parsed=stats.boms_parsed,
            lines_imported=stats.lines_imported,
            warnings_count=stats.warnings_count,
            errors_count=stats.errors_count,
        )
        return stats
    except Exception:
        finish_import_run(conn, run_id, status="failed")
        conn.commit()
        raise


def index_documents(conn: sqlite3.Connection, data_root: Path, run_id: int, force_relink: bool = False) -> None:
    doc_folders = ["PDF", "STEP-DXF", "SOP", "OVERIG"]
    managed_roots = [(data_root / folder).resolve() for folder in doc_folders]
    seen_paths: set[str] = set()
    existing_by_path: dict[str, tuple[int, str]] = {}
    for row in conn.execute("SELECT path, size_bytes, modified_at FROM documents").fetchall():
        path = str(row["path"] or "").strip()
        if not path:
            continue
        existing_by_path[path.casefold()] = (int(row["size_bytes"] or 0), str(row["modified_at"] or ""))
    parts_cache = load_parts_cache(conn)
    token_index = build_parts_token_index(parts_cache)
    for folder in doc_folders:
        folder_path = data_root / folder
        if not folder_path.exists():
            continue
        for file in folder_path.rglob("*"):
            if not file.is_file():
                continue
            resolved_file = str(file.resolve())
            seen_paths.add(resolved_file.casefold())
            stat = file.stat()
            modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="microseconds")
            size_bytes = int(stat.st_size)
            existing = existing_by_path.get(resolved_file.casefold())
            if not force_relink and existing is not None and existing[0] == size_bytes and existing[1] == modified_at:
                continue
            part_id = None
            part_revision = None
            link_reason = None
            part_id, part_revision, link_reason = find_part_match_with_revision(conn, file.name)
            if part_id is None:
                part_id = find_part_id_from_name(conn, file.name, parts_cache=parts_cache, token_index=token_index)
                if part_id is not None:
                    link_reason = "matched_part_fallback"
            if part_id is not None:
                linked_to_type = "part"
                linked_id = part_id
            else:
                linked_to_type = None
                linked_id = None
                if link_reason is None:
                    link_reason = classify_unmatched_reason(conn, file.name)
            upsert_document(
                conn=conn,
                path=resolved_file,
                filename=file.name,
                extension=file.suffix.lower(),
                size_bytes=size_bytes,
                modified_at=modified_at,
                run_id=run_id,
                linked_to_type=linked_to_type,
                linked_id=linked_id,
                doc_type=DOC_EXT_TO_TYPE.get(file.suffix.lower(), "other"),
                part_revision=part_revision,
                link_reason=link_reason,
            )
    remove_missing_documents(conn, managed_roots=managed_roots, seen_paths=seen_paths)
    conn.commit()


def remove_missing_articles(conn: sqlite3.Connection, boms_root: Path) -> int:
    removed = 0
    rows = conn.execute("SELECT id, source_bom_path FROM articles").fetchall()
    for row in rows:
        article_id = int(row["id"])
        raw_path = str(row["source_bom_path"] or "").strip()
        if not raw_path:
            continue
        bom_path = Path(raw_path).resolve()
        if not is_path_within(bom_path, boms_root):
            continue
        if bom_path.exists():
            continue
        conn.execute("DELETE FROM bom_lines WHERE article_id=?", (article_id,))
        conn.execute(
            "DELETE FROM documents WHERE linked_to_type='article' AND linked_id=?",
            (article_id,),
        )
        conn.execute("DELETE FROM articles WHERE id=?", (article_id,))
        removed += 1
    return removed


def remove_missing_documents(conn: sqlite3.Connection, managed_roots: list[Path], seen_paths: set[str]) -> None:
    rows = conn.execute("SELECT id, path FROM documents").fetchall()
    for row in rows:
        raw_path = str(row["path"] or "").strip()
        if not raw_path:
            continue
        doc_path = Path(raw_path).resolve()
        # Always clean stale rows when the file no longer exists.
        # This also removes legacy rows after folder renames (e.g. STEP -> STEP-DXF).
        if not doc_path.exists():
            conn.execute("DELETE FROM documents WHERE id=?", (int(row["id"]),))
            continue
        if not any(is_path_within(doc_path, root) for root in managed_roots):
            continue
        if str(doc_path).casefold() in seen_paths:
            continue
        conn.execute("DELETE FROM documents WHERE id=?", (int(row["id"]),))


def is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_parts_cache(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute("SELECT id, part_number, description FROM parts").fetchall()
    cache: list[dict[str, object]] = []
    for row in rows:
        part_number = str(row["part_number"] or "").strip().upper()
        part_norm = normalize_for_match(part_number)
        desc = str(row["description"] or "").strip()
        desc_norm = normalize_for_match(desc) if desc else ""
        desc_tokens = tokenize_for_match(desc)
        cache.append(
            {
                "id": int(row["id"]),
                "part_number": part_number,
                "part_norm": part_norm,
                "description_norm": desc_norm,
                "description_tokens": desc_tokens,
            }
        )
    cache.sort(key=lambda item: len(str(item["part_norm"])), reverse=True)
    return cache


def normalize_for_match(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def tokenize_for_match(value: str) -> set[str]:
    chunks = TOKEN_SPLIT_REGEX.split(str(value or "").upper())
    tokens: set[str] = set()
    for token in chunks:
        token = token.strip()
        if len(token) < 3:
            continue
        if token.isdigit():
            continue
        if token in COMMON_TOKENS:
            continue
        tokens.add(token)
    return tokens


def build_parts_token_index(parts_cache: list[dict[str, object]]) -> dict[str, set[int]]:
    index: dict[str, set[int]] = {}
    for item in parts_cache:
        part_id = int(item["id"])
        tokens = item.get("description_tokens")
        if not isinstance(tokens, set):
            continue
        for token in tokens:
            bucket = index.setdefault(str(token), set())
            bucket.add(part_id)
    return index


def find_part_id_from_name(
    conn: sqlite3.Connection,
    filename: str,
    parts_cache: list[dict[str, object]] | None = None,
    token_index: dict[str, set[int]] | None = None,
) -> int | None:
    cache = parts_cache if parts_cache is not None else load_parts_cache(conn)
    token_map = token_index if token_index is not None else build_parts_token_index(cache)

    for match in PART_REGEX.finditer(filename):
        row = conn.execute("SELECT id FROM parts WHERE part_number=?", (match.group(1).upper(),)).fetchone()
        if row:
            return int(row["id"])

    filename_norm = normalize_for_match(Path(filename).stem)
    if not filename_norm:
        return None

    # Fallback 1: direct normalized equality (supports descriptive part numbers/text)
    for item in cache:
        part_norm = str(item.get("part_norm") or "")
        if part_norm and part_norm == filename_norm:
            return int(item["id"])

    # Fallback 2: match normalized part number within filename
    for item in cache:
        part_norm = str(item.get("part_norm") or "")
        if len(part_norm) < 4:
            continue
        if part_norm in filename_norm:
            return int(item["id"])

    # Fallback 3: match normalized description phrase in filename
    for item in cache:
        desc_norm = str(item.get("description_norm") or "")
        if len(desc_norm) < 8:
            continue
        if desc_norm in filename_norm:
            return int(item["id"])

    # Fallback 4: token-overlap match between filename and part description.
    # This supports descriptive filenames where token order differs.
    filename_tokens = tokenize_for_match(Path(filename).stem)
    if not filename_tokens:
        return None
    candidate_ids: set[int] = set()
    for token in filename_tokens:
        candidate_ids.update(token_map.get(token, set()))
    if not candidate_ids:
        return None
    by_id = {int(item["id"]): item for item in cache}
    best_id: int | None = None
    best_score = 0.0
    second_score = 0.0
    for part_id in candidate_ids:
        item = by_id.get(part_id)
        if not item:
            continue
        desc_tokens = item.get("description_tokens")
        if not isinstance(desc_tokens, set) or not desc_tokens:
            continue
        overlap = len(filename_tokens.intersection(desc_tokens))
        if overlap < 2:
            continue
        score = overlap / float(max(1, len(desc_tokens)))
        if score > best_score:
            second_score = best_score
            best_score = score
            best_id = part_id
        elif score > second_score:
            second_score = score
    if best_id is None:
        return None
    # Require a clear winner to avoid wrong links.
    if second_score > 0.0 and (best_score - second_score) < 0.20:
        return None
    if best_score < 0.35:
        return None
    return best_id


def find_part_match_with_revision(conn: sqlite3.Connection, filename: str) -> tuple[int | None, str | None, str | None]:
    parsed = parse_document_part_and_revision(filename)
    if not parsed:
        return None, None, None
    part_number, revision = parsed
    row = conn.execute("SELECT id FROM parts WHERE part_number=?", (part_number,)).fetchone()
    if not row:
        return None, None, "part_not_found_in_bom_index"
    part_id = int(row["id"])
    if revision:
        exists = conn.execute(
            "SELECT 1 FROM bom_lines WHERE part_id=? AND UPPER(COALESCE(revision, ''))=? LIMIT 1",
            (part_id, revision),
        ).fetchone()
        if not exists:
            return None, None, "revision_mismatch"
        return part_id, revision, "matched_part_and_revision"

    rev_stats = conn.execute(
        """
        SELECT COUNT(DISTINCT UPPER(COALESCE(revision, ''))) AS rev_count,
               SUM(CASE WHEN COALESCE(TRIM(revision), '') = '' THEN 1 ELSE 0 END) AS empty_count
        FROM bom_lines
        WHERE part_id=?
        """,
        (part_id,),
    ).fetchone()
    if not rev_stats:
        return part_id, None, "matched_part_no_revision"
    if int(rev_stats["empty_count"] or 0) > 0:
        return part_id, None, "matched_part_no_revision"
    if int(rev_stats["rev_count"] or 0) <= 1:
        return part_id, None, "matched_part_single_revision"
    return None, None, "ambiguous_revision_required"


def parse_document_part_and_revision(filename: str) -> tuple[str, str | None] | None:
    stem = Path(filename).stem.upper()
    part_match = DOC_PART_PATTERN.search(stem)
    if not part_match:
        return None
    part_number = part_match.group(1)
    revision = None

    rev_match = re.search(r"[_\-]REV[_\-]?([A-Z0-9]+)\b", stem)
    if not rev_match:
        rev_match = re.search(rf"{re.escape(part_number)}[_\-]([A-Z0-9]+)\b", stem)
    if not rev_match:
        rev_match = re.search(r"[_\-]R([A-Z0-9]+)\b", stem)
    if rev_match:
        revision = rev_match.group(1).strip().upper()
    return part_number, revision


def classify_unmatched_reason(conn: sqlite3.Connection, filename: str) -> str:
    parsed = parse_document_part_and_revision(filename)
    if not parsed:
        return "no_part_token_in_filename"
    part_number, revision = parsed
    part = conn.execute("SELECT id FROM parts WHERE part_number=?", (part_number,)).fetchone()
    if not part:
        return "part_not_found_in_bom_index"
    if revision:
        return "revision_mismatch"
    return "ambiguous_or_missing_revision"
