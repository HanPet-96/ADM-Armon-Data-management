from adm_app.mapping import map_headers, parse_qty


def test_map_headers_handles_synonyms():
    headers = ["Part No", "Omschrijving", "Aantal", "Rev", "Materiaal", "Finish", "Type", "Status", "Item No."]
    mapping = map_headers(headers)
    assert mapping[0] == "part_number"
    assert mapping[1] == "description"
    assert mapping[2] == "qty"
    assert mapping[3] == "revision"
    assert mapping[4] == "material"
    assert mapping[5] == "finish"
    assert mapping[6] == "line_type"
    assert mapping[7] == "status"
    assert mapping[8] == "line_no"


def test_parse_qty_supports_comma_decimal():
    assert parse_qty("1,5") == 1.5
    assert parse_qty("2") == 2.0
    assert parse_qty("") is None
