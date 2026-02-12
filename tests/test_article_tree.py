from adm_app.db import get_connection, init_db, insert_bom_line, upsert_article, upsert_part
from adm_app.search import get_child_articles, get_parent_articles


def test_get_child_articles_detects_subassemblies(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    parent_id = upsert_article(conn, "1000", "Root", "x", "x")
    child_id = upsert_article(conn, "500", "Child", "y", "y")
    part_id = upsert_part(conn, "500", "Subassembly part")
    run_id = conn.execute("INSERT INTO import_runs(status) VALUES ('completed')").lastrowid
    insert_bom_line(
        conn=conn,
        article_id=parent_id,
        part_id=part_id,
        line_no=10,
        qty=1.0,
        unit=None,
        revision="A",
        description="Subassembly",
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

    children = get_child_articles(conn, parent_id)
    assert len(children) == 1
    assert int(children[0]["child_article_id"]) == child_id
    assert children[0]["article_number"] == "500"

    parents = get_parent_articles(conn, child_id)
    assert len(parents) == 1
    assert int(parents[0]["parent_article_id"]) == parent_id
