from __future__ import annotations

import sqlite3


def list_articles(
    conn: sqlite3.Connection, query: str = "", limit: int = 500, search_in_children: bool = True
) -> list[sqlite3.Row]:
    if query.strip():
        q = f"%{query.strip()}%"
        if search_in_children:
            where_clauses = [
                "(a.article_number LIKE ? OR COALESCE(a.title, '') LIKE ? OR COALESCE(p.part_number, '') LIKE ? OR COALESCE(p.description, '') LIKE ?)"
            ]
            params: list[object] = [q, q, q, q]
        else:
            where_clauses = ["(a.article_number LIKE ? OR COALESCE(a.title, '') LIKE ?)"]
            params = [q, q]
        where_sql = " AND ".join(where_clauses)
        params.append(limit)
        return conn.execute(
            """
            SELECT
                a.id,
                a.article_number,
                a.title,
                COUNT(bl.id) AS bom_line_count
            FROM articles a
            LEFT JOIN bom_lines bl ON bl.article_id = a.id
            LEFT JOIN parts p ON p.id = bl.part_id
            WHERE
            """
            + where_sql
            + """
            GROUP BY a.id, a.article_number, a.title
            ORDER BY a.article_number
            LIMIT ?
            """,
            params,
        ).fetchall()
    return conn.execute(
        """
        SELECT a.id, a.article_number, a.title, COUNT(bl.id) AS bom_line_count
        FROM articles a
        LEFT JOIN bom_lines bl ON bl.article_id = a.id
        GROUP BY a.id, a.article_number, a.title
        ORDER BY a.article_number
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def get_article(conn: sqlite3.Connection, article_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()


def get_article_by_number(conn: sqlite3.Connection, article_number: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM articles WHERE article_number=?", (article_number,)).fetchone()


def get_article_ids_by_numbers(conn: sqlite3.Connection, article_numbers: list[str]) -> dict[str, int]:
    normalized = [str(n).strip() for n in article_numbers if str(n).strip()]
    if not normalized:
        return {}
    placeholders = ",".join(["?"] * len(normalized))
    rows = conn.execute(
        f"SELECT id, article_number FROM articles WHERE article_number IN ({placeholders})",
        normalized,
    ).fetchall()
    return {str(row["article_number"]): int(row["id"]) for row in rows}


def get_article_bom_lines(conn: sqlite3.Connection, article_id: int) -> list[sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT
            bl.id,
            bl.part_id,
            bl.item_no,
            bl.line_no,
            p.part_number,
            COALESCE(bl.description, p.description) AS description,
            bl.qty,
            bl.unit,
            bl.revision,
            bl.material,
            bl.finish,
            bl.line_type,
            bl.status,
            bl.source_sheet,
            bl.source_row_number
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        WHERE bl.article_id=?
        """,
        (article_id,),
    ).fetchall()
    return sorted(rows, key=bom_line_sort_key)


def bom_line_sort_key(row: sqlite3.Row) -> tuple:
    item_no = str(row["item_no"] or "").strip()
    if item_no:
        parts: list[tuple[int, int | str]] = []
        for token in item_no.split("."):
            if token.isdigit():
                parts.append((0, int(token)))
            else:
                parts.append((1, token))
        return (0, tuple(parts), str(row["part_number"] or ""))
    line_no = row["line_no"]
    if line_no is not None:
        return (1, ((0, int(line_no)),), str(row["part_number"] or ""))
    return (2, tuple(), str(row["part_number"] or ""))


def get_documents_for_link(conn: sqlite3.Connection, linked_to_type: str, linked_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT * FROM documents
        WHERE linked_to_type=? AND linked_id=?
        ORDER BY filename
        """,
        (linked_to_type, linked_id),
    ).fetchall()


def get_part_detail(conn: sqlite3.Connection, part_number: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM parts WHERE part_number=?", (part_number,)).fetchone()


def get_part_usages(conn: sqlite3.Connection, part_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            a.article_number,
            a.title,
            bl.qty,
            bl.revision,
            bl.material
        FROM bom_lines bl
        JOIN articles a ON a.id = bl.article_id
        WHERE bl.part_id=?
        ORDER BY a.article_number
        """,
        (part_id,),
    ).fetchall()


def get_documents_for_part_revision(
    conn: sqlite3.Connection, part_id: int, revision: str | None
) -> list[sqlite3.Row]:
    if revision and str(revision).strip():
        rev = str(revision).strip().upper()
        rows = conn.execute(
            """
            SELECT * FROM documents
            WHERE linked_to_type='part' AND linked_id=? AND UPPER(COALESCE(part_revision, ''))=?
            ORDER BY filename
            """,
            (part_id, rev),
        ).fetchall()
        if rows:
            return rows
    return conn.execute(
        """
        SELECT * FROM documents
        WHERE linked_to_type='part' AND linked_id=?
        ORDER BY filename
        """,
        (part_id,),
    ).fetchall()


def get_unlinked_documents(conn: sqlite3.Connection, limit: int = 500) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT filename, path, extension, link_reason
        FROM documents
        WHERE linked_to_type IS NULL
        ORDER BY filename
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def get_articles_using_part_number(conn: sqlite3.Connection, part_number: str) -> list[sqlite3.Row]:
    value = str(part_number or "").strip()
    if not value:
        return []
    return conn.execute(
        """
        SELECT
            a.id AS article_id,
            a.article_number,
            a.title,
            bl.item_no,
            bl.qty,
            bl.revision,
            p.part_number
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        JOIN articles a ON a.id = bl.article_id
        WHERE UPPER(p.part_number) = UPPER(?)
        ORDER BY a.article_number, bl.item_no
        """,
        (value,),
    ).fetchall()


def get_parent_articles_for_part_candidates(conn: sqlite3.Connection, candidates: list[str]) -> list[sqlite3.Row]:
    normalized = sorted({str(v).strip().upper() for v in candidates if str(v).strip()})
    if not normalized:
        return []
    placeholders = ",".join(["?"] * len(normalized))
    return conn.execute(
        f"""
        SELECT
            a.id AS article_id,
            a.article_number,
            a.title,
            bl.item_no,
            p.part_number,
            bl.qty,
            bl.revision
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        JOIN articles a ON a.id = bl.article_id
        WHERE UPPER(p.part_number) IN ({placeholders})
        ORDER BY a.article_number, bl.item_no, p.part_number
        """,
        normalized,
    ).fetchall()


def get_parent_articles_for_part_candidates_like(conn: sqlite3.Connection, candidates: list[str]) -> list[sqlite3.Row]:
    normalized = sorted({str(v).strip().upper() for v in candidates if str(v).strip()})
    if not normalized:
        return []
    like_clauses = " OR ".join(["UPPER(p.part_number) LIKE ?"] * len(normalized))
    params: list[object] = [f"%{value}%" for value in normalized]
    return conn.execute(
        f"""
        SELECT
            a.id AS article_id,
            a.article_number,
            a.title,
            bl.item_no,
            p.part_number,
            bl.qty,
            bl.revision
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        JOIN articles a ON a.id = bl.article_id
        WHERE ({like_clauses})
        ORDER BY a.article_number, bl.item_no, p.part_number
        """,
        params,
    ).fetchall()
