from adm_app.db import get_connection, init_db, insert_bom_line, upsert_article, upsert_part
from adm_app.search import list_articles


def test_list_articles_top_level_filter(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    parent_id = upsert_article(conn, "1000", "Parent", "x", "x")
    upsert_article(conn, "500", "Child", "y", "y")
    part_id = upsert_part(conn, "500", "Child as part")
    run_id = conn.execute("INSERT INTO import_runs(status) VALUES ('completed')").lastrowid
    insert_bom_line(
        conn=conn,
        article_id=parent_id,
        part_id=part_id,
        line_no=1,
        qty=1.0,
        unit=None,
        revision="A",
        description="child",
        material=None,
        finish=None,
        line_type=None,
        status=None,
        raw_columns={},
        source_sheet="BOM",
        source_row_number=2,
        run_id=int(run_id),
    )
    conn.commit()

    all_articles = list_articles(conn, top_level_only=False)
    top_level_articles = list_articles(conn, top_level_only=True)
    all_numbers = {row["article_number"] for row in all_articles}
    top_numbers = {row["article_number"] for row in top_level_articles}
    assert {"1000", "500"}.issubset(all_numbers)
    assert "1000" in top_numbers
    assert "500" not in top_numbers

