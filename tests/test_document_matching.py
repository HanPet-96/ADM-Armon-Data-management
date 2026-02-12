from adm_app.db import get_connection, init_db, upsert_article, upsert_part
from adm_app.indexer import find_part_match_with_revision, parse_document_part_and_revision


def test_parse_document_part_and_revision():
    assert parse_document_part_and_revision("15-00407_B.PDF") == ("15-00407", "B")
    assert parse_document_part_and_revision("13-00023_rev-C.pdf") == ("13-00023", "C")
    assert parse_document_part_and_revision("15-00503.step") == ("15-00503", None)
    assert parse_document_part_and_revision("manual.pdf") is None


def test_find_part_match_with_revision(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    article_id = upsert_article(conn, "17001", "Test", "x", "x")
    part_id = upsert_part(conn, "15-00407", "Bracket")
    conn.execute(
        """
        INSERT INTO bom_lines(article_id, part_id, revision, source_sheet, source_row_number)
        VALUES (?, ?, 'B', 'BOM', 2)
        """,
        (article_id, part_id),
    )
    conn.commit()

    linked_part_id, rev, reason = find_part_match_with_revision(conn, "15-00407_B.PDF")
    assert linked_part_id == part_id
    assert rev == "B"
    assert reason == "matched_part_and_revision"

    no_link_id, no_link_rev, no_link_reason = find_part_match_with_revision(conn, "15-00407_A.PDF")
    assert no_link_id is None
    assert no_link_rev is None
    assert no_link_reason == "revision_mismatch"
