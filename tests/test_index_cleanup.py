from pathlib import Path

from adm_app.db import get_connection, init_db, upsert_article
from adm_app.indexer import remove_missing_articles


def test_remove_missing_articles_removes_stale_rows(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)

    boms_root = tmp_path / "Datastruct" / "BOMS"
    boms_root.mkdir(parents=True, exist_ok=True)
    existing_bom = boms_root / "BOM 1000 Existing.xlsx"
    existing_bom.write_bytes(b"dummy")

    stale_bom = boms_root / "BOM 2000 Stale.xlsx"

    upsert_article(conn, "1000", "Existing", str(existing_bom.resolve()), existing_bom.name)
    stale_id = upsert_article(conn, "2000", "Stale", str(stale_bom.resolve()), stale_bom.name)
    conn.execute(
        """
        INSERT INTO parts(part_number, description) VALUES ('X-1', 'x')
        """
    )
    part_id = int(conn.execute("SELECT id FROM parts WHERE part_number='X-1'").fetchone()["id"])
    conn.execute(
        """
        INSERT INTO bom_lines(article_id, part_id, source_sheet, source_row_number)
        VALUES (?, ?, 'BOM', 1)
        """,
        (stale_id, part_id),
    )
    conn.commit()

    remove_missing_articles(conn, boms_root.resolve())
    conn.commit()

    numbers = {row["article_number"] for row in conn.execute("SELECT article_number FROM articles").fetchall()}
    assert "1000" in numbers
    assert "2000" not in numbers
    stale_lines = conn.execute("SELECT COUNT(*) AS c FROM bom_lines WHERE article_id=?", (stale_id,)).fetchone()["c"]
    assert int(stale_lines) == 0
