from __future__ import annotations

import sqlite3


def list_articles(
    conn: sqlite3.Connection, query: str = "", limit: int = 500, top_level_only: bool = False
) -> list[sqlite3.Row]:
    top_level_filter = """
        NOT EXISTS (
            SELECT 1
            FROM parts p2
            JOIN bom_lines bl2 ON bl2.part_id = p2.id
            WHERE p2.part_number = a.article_number
        )
    """
    if query.strip():
        q = f"%{query.strip()}%"
        where_clauses = [
            "(a.article_number LIKE ? OR COALESCE(a.title, '') LIKE ? OR COALESCE(p.part_number, '') LIKE ? OR COALESCE(p.description, '') LIKE ?)"
        ]
        params: list[object] = [q, q, q, q]
        if top_level_only:
            where_clauses.append(top_level_filter)
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
    where_sql = f"WHERE {top_level_filter}" if top_level_only else ""
    return conn.execute(
        """
        SELECT a.id, a.article_number, a.title, COUNT(bl.id) AS bom_line_count
        FROM articles a
        LEFT JOIN bom_lines bl ON bl.article_id = a.id
        """
        + where_sql
        + """
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


def get_article_bom_lines(conn: sqlite3.Connection, article_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            bl.id,
            bl.part_id,
            bl.line_no,
            p.part_number,
            COALESCE(bl.description, p.description) AS description,
            bl.qty,
            bl.unit,
            bl.revision,
            bl.material,
            bl.finish,
            bl.line_type,
            bl.status
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        WHERE bl.article_id=?
        ORDER BY COALESCE(bl.line_no, 999999), p.part_number
        """,
        (article_id,),
    ).fetchall()


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


def get_child_articles(conn: sqlite3.Connection, parent_article_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            child.id AS child_article_id,
            child.article_number,
            child.title,
            SUM(COALESCE(bl.qty, 1)) AS qty_total
        FROM bom_lines bl
        JOIN parts p ON p.id = bl.part_id
        JOIN articles child ON child.article_number = p.part_number
        WHERE bl.article_id=?
        GROUP BY child.id, child.article_number, child.title
        ORDER BY child.article_number
        """,
        (parent_article_id,),
    ).fetchall()


def get_parent_articles(conn: sqlite3.Connection, child_article_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            parent.id AS parent_article_id,
            parent.article_number,
            parent.title,
            SUM(COALESCE(bl.qty, 1)) AS qty_total
        FROM articles child
        JOIN parts p ON p.part_number = child.article_number
        JOIN bom_lines bl ON bl.part_id = p.id
        JOIN articles parent ON parent.id = bl.article_id
        WHERE child.id=?
        GROUP BY parent.id, parent.article_number, parent.title
        ORDER BY parent.article_number
        """,
        (child_article_id,),
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
