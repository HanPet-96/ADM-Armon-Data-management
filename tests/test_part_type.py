import pytest

from adm_app.db import get_connection, init_db, update_part_type, upsert_part


def test_update_part_type_valid_and_invalid(tmp_path):
    conn = get_connection(tmp_path / "adm_test.db")
    init_db(conn)
    part_id = upsert_part(conn, "SCREW-001", "Screw")

    update_part_type(conn, part_id, "fastener")
    row = conn.execute("SELECT part_type FROM parts WHERE id=?", (part_id,)).fetchone()
    assert row["part_type"] == "fastener"

    update_part_type(conn, part_id, "")
    row = conn.execute("SELECT part_type FROM parts WHERE id=?", (part_id,)).fetchone()
    assert row["part_type"] is None

    with pytest.raises(ValueError):
        update_part_type(conn, part_id, "invalid_type")

