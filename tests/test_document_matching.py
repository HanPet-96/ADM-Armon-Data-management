from pathlib import Path

from adm_app.db import get_connection, init_db, upsert_article, upsert_document, upsert_part
from adm_app.indexer import find_part_match_with_revision, index_documents, parse_document_part_and_revision


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


def test_index_documents_removes_missing_files(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)

    data_root = tmp_path / "Datastruct"
    pdf_dir = data_root / "PDF"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    current_file = pdf_dir / "15-00407_B.pdf"
    current_file.write_bytes(b"%PDF-1.4\n%")

    stale_file = pdf_dir / "old_file.pdf"
    run_id = conn.execute("INSERT INTO import_runs(status) VALUES ('completed')").lastrowid
    upsert_document(
        conn=conn,
        path=str(stale_file.resolve()),
        filename=stale_file.name,
        extension=".pdf",
        size_bytes=10,
        modified_at="2026-01-01T00:00:00",
        run_id=int(run_id),
        linked_to_type=None,
        linked_id=None,
        doc_type="pdf",
        part_revision=None,
        link_reason="seed",
    )
    conn.commit()

    index_documents(conn, Path(data_root), int(run_id))

    rows = conn.execute("SELECT path FROM documents ORDER BY path").fetchall()
    paths = {str(row["path"]) for row in rows}
    assert str(current_file.resolve()) in paths
    assert str(stale_file.resolve()) not in paths
