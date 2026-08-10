"""测试格式转换"""

import csv
import os
import sys
import openpyxl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from excel_tools.format_converter import convert_to_csv


HEADERS = ["Name", "Age"]
ROWS = [
    ["Alice", 25],
    ["Bob", 30],
]


def _make_xlsx(headers, rows, path):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


@pytest.fixture
def sample_xlsx(tmp_path):
    path = os.path.join(tmp_path, "test_convert.xlsx")
    _make_xlsx(HEADERS, ROWS, path)
    return path


class TestConvertToCsv:
    def test_convert_excel_to_csv(self, sample_xlsx):
        result = convert_to_csv(sample_xlsx)
        assert result.endswith(".csv")
        assert os.path.exists(result)
        with open(result, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            content = list(reader)
        assert len(content) == 3
        assert content[0] == HEADERS

    def test_convert_with_custom_path(self, sample_xlsx, tmp_path):
        out = os.path.join(tmp_path, "custom.csv")
        result = convert_to_csv(sample_xlsx, out)
        assert result == out
        assert os.path.exists(out)

    def test_convert_csv_to_csv(self, tmp_path):
        csv_in = os.path.join(tmp_path, "input.csv")
        with open(csv_in, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEADERS)
            w.writerows(ROWS)
        out = os.path.join(tmp_path, "output.csv")
        convert_to_csv(csv_in, out)
        assert os.path.exists(out)

    def test_encoding(self, sample_xlsx, tmp_path):
        out = os.path.join(tmp_path, "encoded.csv")
        convert_to_csv(sample_xlsx, out, encoding="gbk")
        with open(out, "r", encoding="gbk") as f:
            content = f.read()
        assert "Name" in content
