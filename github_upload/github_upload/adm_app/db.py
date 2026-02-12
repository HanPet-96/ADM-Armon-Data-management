from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_number TEXT NOT NULL UNIQUE,
    title TEXT,
    source_bom_filename TEXT,
    source_bom_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL UNIQUE,
    description TEXT,
    part_type TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    status TEXT NOT NULL,
    files_scanned INTEGER DEFAULT 0,
    boms_parsed INTEGER DEFAULT 0,
    lines_imported INTEGER DEFAULT 0,
    warnings_count INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bom_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    line_no INTEGER,
    qty REAL,
    unit TEXT,
    revision TEXT,
    description TEXT,
    material TEXT,
    finish TEXT,
    line_type TEXT,
    status TEXT,
    raw_columns_json TEXT,
    source_sheet TEXT,
    source_row_number INTEGER,
    import_run_id INTEGER,
    FOREIGN KEY(article_id) REFERENCES articles(id),
    FOREIGN KEY(part_id) REFERENCES parts(id),
    FOREIGN KEY(import_run_id) REFERENCES import_runs(id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    linked_to_type TEXT,
    linked_id INTEGER,
    doc_type TEXT,
    filename TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    extension TEXT,
    size_bytes INTEGER,
    modified_at TEXT,
    sha256 TEXT,
    import_run_id INTEGER,
    FOREIGN KEY(import_run_id) REFERENCES import_runs(id)
);

CREATE TABLE IF NOT EXISTS import_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_run_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    file_path TEXT,
    sheet_name TEXT,
    row_number INTEGER,
    message TEXT NOT NULL,
    raw_row_json TEXT,
    FOREIGN KEY(import_run_id) REFERENCES import_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_articles_number ON articles(article_number);
CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number);
CREATE INDEX IF NOT EXISTS idx_bom_article ON bom_lines(article_id);
CREATE INDEX IF NOT EXISTS idx_bom_part ON bom_lines(part_id);
CREATE INDEX IF NOT EXISTS idx_documents_link ON documents(linked_to_type, linked_id);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    ensure_bom_lines_columns(conn)
    ensure_documents_columns(conn)
    conn.commit()


def ensure_bom_lines_columns(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(bom_lines)").fetchall()}
    if "finish" not in columns:
        conn.execute("ALTER TABLE bom_lines ADD COLUMN finish TEXT")
    if "line_type" not in columns:
        conn.execute("ALTER TABLE bom_lines ADD COLUMN line_type TEXT")
    if "status" not in columns:
        conn.execute("ALTER TABLE bom_lines ADD COLUMN status TEXT")


def ensure_documents_columns(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(documents)").fetchall()}
    if "part_revision" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN part_revision TEXT")
    if "link_reason" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN link_reason TEXT")


def start_import_run(conn: sqlite3.Connection) -> int:
    cur = conn.execute("INSERT INTO import_runs(status) VALUES ('running')")
    conn.commit()
    return int(cur.lastrowid)


def finish_import_run(conn: sqlite3.Connection, run_id: int, **stats: Any) -> None:
    updates = ["finished_at=CURRENT_TIMESTAMP", "status=:status"]
    params: dict[str, Any] = {"id": run_id, "status": stats.get("status", "completed")}
    for key in (
        "files_scanned",
        "boms_parsed",
        "lines_imported",
        "warnings_count",
        "errors_count",
    ):
        if key in stats:
            updates.append(f"{key}=:{key}")
            params[key] = stats[key]
    conn.execute(f"UPDATE import_runs SET {', '.join(updates)} WHERE id=:id", params)
    conn.commit()


def log_issue(
    conn: sqlite3.Connection,
    run_id: int,
    severity: str,
    message: str,
    file_path: str | None = None,
    sheet_name: str | None = None,
    row_number: int | None = None,
    raw_row: dict[str, Any] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO import_issues(import_run_id, severity, file_path, sheet_name, row_number, message, raw_row_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            severity,
            file_path,
            sheet_name,
            row_number,
            message,
            json.dumps(raw_row, ensure_ascii=True) if raw_row is not None else None,
        ),
    )


def upsert_article(
    conn: sqlite3.Connection,
    article_number: str,
    title: str | None,
    source_bom_path: str,
    source_bom_filename: str,
) -> int:
    conn.execute(
        """
        INSERT INTO articles(article_number, title, source_bom_filename, source_bom_path, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(article_number) DO UPDATE SET
            title=excluded.title,
            source_bom_filename=excluded.source_bom_filename,
            source_bom_path=excluded.source_bom_path,
            updated_at=CURRENT_TIMESTAMP
        """,
        (article_number, title, source_bom_filename, source_bom_path),
    )
    cur = conn.execute("SELECT id FROM articles WHERE article_number=?", (article_number,))
    row = cur.fetchone()
    return int(row["id"])


def upsert_part(conn: sqlite3.Connection, part_number: str, description: str | None) -> int:
    conn.execute(
        """
        INSERT INTO parts(part_number, description, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(part_number) DO UPDATE SET
            description=COALESCE(excluded.description, parts.description),
            updated_at=CURRENT_TIMESTAMP
        """,
        (part_number, description),
    )
    cur = conn.execute("SELECT id FROM parts WHERE part_number=?", (part_number,))
    row = cur.fetchone()
    return int(row["id"])


def insert_bom_line(
    conn: sqlite3.Connection,
    article_id: int,
    part_id: int,
    line_no: int | None,
    qty: float | None,
    unit: str | None,
    revision: str | None,
    description: str | None,
    material: str | None,
    finish: str | None,
    line_type: str | None,
    status: str | None,
    raw_columns: dict[str, Any],
    source_sheet: str,
    source_row_number: int,
    run_id: int,
) -> None:
    conn.execute(
        """
        INSERT INTO bom_lines(
            article_id, part_id, line_no, qty, unit, revision, description, material,
            finish, line_type, status, raw_columns_json, source_sheet, source_row_number, import_run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article_id,
            part_id,
            line_no,
            qty,
            unit,
            revision,
            description,
            material,
            finish,
            line_type,
            status,
            json.dumps(raw_columns, ensure_ascii=True),
            source_sheet,
            source_row_number,
            run_id,
        ),
    )


def clear_article_lines_for_run(conn: sqlite3.Connection, article_id: int) -> None:
    conn.execute("DELETE FROM bom_lines WHERE article_id=?", (article_id,))


def upsert_document(
    conn: sqlite3.Connection,
    path: str,
    filename: str,
    extension: str,
    size_bytes: int,
    modified_at: str,
    run_id: int,
    linked_to_type: str | None = None,
    linked_id: int | None = None,
    doc_type: str | None = None,
    part_revision: str | None = None,
    link_reason: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO documents(path, filename, extension, size_bytes, modified_at, import_run_id, linked_to_type, linked_id, doc_type, part_revision, link_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            filename=excluded.filename,
            extension=excluded.extension,
            size_bytes=excluded.size_bytes,
            modified_at=excluded.modified_at,
            import_run_id=excluded.import_run_id,
            linked_to_type=excluded.linked_to_type,
            linked_id=excluded.linked_id,
            doc_type=excluded.doc_type,
            part_revision=excluded.part_revision,
            link_reason=excluded.link_reason
        """,
        (
            path,
            filename,
            extension,
            size_bytes,
            modified_at,
            run_id,
            linked_to_type,
            linked_id,
            doc_type,
            part_revision,
            link_reason,
        ),
    )


VALID_PART_TYPES = {
    "mechanical",
    "fastener",
    "packaging",
    "label",
    "documentation",
    "service",
    "other",
}


def update_part_type(conn: sqlite3.Connection, part_id: int, part_type: str | None) -> None:
    normalized = None if part_type in (None, "") else part_type.strip().lower()
    if normalized is not None and normalized not in VALID_PART_TYPES:
        raise ValueError(f"Invalid part_type: {part_type}")
    conn.execute(
        """
        UPDATE parts
        SET part_type=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (normalized, part_id),
    )
    conn.commit()
