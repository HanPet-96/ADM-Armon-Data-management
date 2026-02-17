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


def run_index(conn: sqlite3.Connection, data_root: Path) -> IndexStats:
    stats = IndexStats()
    run_id = start_import_run(conn)
    try:
        boms_path = data_root / "BOMS"
        bom_files = sorted(
            [*boms_path.rglob("*.xlsx"), *boms_path.rglob("*.xls"), *boms_path.rglob("*.xlsm")]
        )
        stats.files_scanned += len(bom_files)
        for bom_file in bom_files:
            try:
                parsed = parse_bom_file(bom_file)
                article_id = upsert_article(
                    conn,
                    article_number=parsed.article_number,
                    title=parsed.article_title,
                    source_bom_path=str(parsed.source_file),
                    source_bom_filename=parsed.source_file.name,
                )
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
        remove_missing_articles(conn, boms_root=boms_path.resolve())
        index_documents(conn, data_root, run_id)
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


def index_documents(conn: sqlite3.Connection, data_root: Path, run_id: int) -> None:
    doc_folders = ["PDF", "STEP", "SOP", "OVERIG"]
    managed_roots = [(data_root / folder).resolve() for folder in doc_folders]
    seen_paths: set[str] = set()
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
            part_id = None
            part_revision = None
            link_reason = None
            part_id, part_revision, link_reason = find_part_match_with_revision(conn, file.name)
            if part_id is None:
                part_id = find_part_id_from_name(conn, file.name)
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
                size_bytes=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                run_id=run_id,
                linked_to_type=linked_to_type,
                linked_id=linked_id,
                doc_type=DOC_EXT_TO_TYPE.get(file.suffix.lower(), "other"),
                part_revision=part_revision,
                link_reason=link_reason,
            )
    remove_missing_documents(conn, managed_roots=managed_roots, seen_paths=seen_paths)
    conn.commit()


def remove_missing_articles(conn: sqlite3.Connection, boms_root: Path) -> None:
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


def remove_missing_documents(conn: sqlite3.Connection, managed_roots: list[Path], seen_paths: set[str]) -> None:
    rows = conn.execute("SELECT id, path FROM documents").fetchall()
    for row in rows:
        raw_path = str(row["path"] or "").strip()
        if not raw_path:
            continue
        doc_path = Path(raw_path).resolve()
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


def find_part_id_from_name(conn: sqlite3.Connection, filename: str) -> int | None:
    for match in PART_REGEX.finditer(filename):
        row = conn.execute("SELECT id FROM parts WHERE part_number=?", (match.group(1).upper(),)).fetchone()
        if row:
            return int(row["id"])
    return None


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
