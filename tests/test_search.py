from adm_app.db import get_connection, init_db, upsert_article, upsert_part
from adm_app.search import get_article_bom_lines, list_articles


def test_list_articles_basic(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    upsert_article(conn, "1000", "Parent", "x", "x")
    upsert_article(conn, "500", "Child", "y", "y")
    conn.commit()

    all_articles = list_articles(conn)
    all_numbers = {row["article_number"] for row in all_articles}
    assert {"1000", "500"}.issubset(all_numbers)


def test_get_article_bom_lines_sorts_by_item_hierarchy(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    article_id = upsert_article(conn, "17004", "Leva", "x", "x")
    part_a = upsert_part(conn, "PART-A", "a")
    part_b = upsert_part(conn, "PART-B", "b")
    part_c = upsert_part(conn, "PART-C", "c")
    run_id = int(conn.execute("INSERT INTO import_runs(status) VALUES ('completed')").lastrowid)
    conn.execute(
        "INSERT INTO bom_lines(article_id, part_id, item_no, source_sheet, source_row_number, import_run_id) VALUES (?, ?, ?, 'BOM', 1, ?)",
        (article_id, part_c, "4.32.2", run_id),
    )
    conn.execute(
        "INSERT INTO bom_lines(article_id, part_id, item_no, source_sheet, source_row_number, import_run_id) VALUES (?, ?, ?, 'BOM', 2, ?)",
        (article_id, part_a, "4", run_id),
    )
    conn.execute(
        "INSERT INTO bom_lines(article_id, part_id, item_no, source_sheet, source_row_number, import_run_id) VALUES (?, ?, ?, 'BOM', 3, ?)",
        (article_id, part_b, "4.32.1", run_id),
    )
    conn.commit()

    rows = get_article_bom_lines(conn, article_id)
    assert [row["item_no"] for row in rows] == ["4", "4.32.1", "4.32.2"]
