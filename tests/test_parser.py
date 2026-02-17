from pathlib import Path

from openpyxl import Workbook

from adm_app.excel_parser import extract_article_from_filename, parse_bom_file


def test_extract_article_from_filename():
    article, title = extract_article_from_filename("BOM 17004 Leva single.xls")
    assert article == "17004"
    assert "Leva single" in title
    article2, _ = extract_article_from_filename("BOM 500 Demo Child.xlsx")
    assert article2 == "500"


def test_parse_bom_xlsx(tmp_path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "BOM"
    ws.append(["Item No.", "Part Number", "Revision", "Description", "Material", "Finish", "Qty", "Type", "Status"])
    ws.append([10, "SCREW-001", "A", "Screw M4", "Steel", "Zinc", 4, "hardware", "Approved"])
    ws.append(["4.32.1", "KNOB-001", "B", "Adjust knob sub", "Plastic", "", 1, "mechanical", "Released"])
    ws.append([20, "PLATE-123", "B", "Plate", "Aluminum", "Anodized", "1,5", "mechanical", "Denied"])
    path = tmp_path / "BOM 17001 Test.xlsx"
    wb.save(path)

    parsed = parse_bom_file(path)
    assert parsed.article_number == "17001"
    assert len(parsed.lines) == 3
    assert parsed.lines[0].part_number == "SCREW-001"
    assert parsed.lines[0].item_no == "10"
    assert parsed.lines[0].qty == 4.0
    assert parsed.lines[0].finish == "Zinc"
    assert parsed.lines[0].line_type == "hardware"
    assert parsed.lines[0].status == "Approved"
    assert parsed.lines[1].item_no == "4.32.1"
    assert parsed.lines[2].qty == 1.5
