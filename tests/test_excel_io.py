"""测试 excel_io 读写与标题检测"""

import os
import sys
import openpyxl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from excel_tools.excel_io import read_table, read_headers, write_table


def _make_xlsx(rows, path):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


class TestTitleDetection:
    def test_normal_header(self, tmp_path):
        path = os.path.join(tmp_path, "a.xlsx")
        _make_xlsx([["Name", "Age"], ["Alice", 25], ["Bob", 30]], path)
        headers, rows = read_table(path)
        assert headers == ["Name", "Age"]
        assert len(rows) == 2

    def test_title_row_skipped(self, tmp_path):
        path = os.path.join(tmp_path, "b.xlsx")
        _make_xlsx([["销售数据表", None], ["Name", "Age"], ["Alice", 25]], path)
        headers, rows = read_table(path)
        assert headers == ["Name", "Age"]
        assert len(rows) == 1

    def test_read_headers_title(self, tmp_path):
        path = os.path.join(tmp_path, "c.xlsx")
        _make_xlsx([["标题", None], ["ColA", "ColB"], ["x", "y"]], path)
        assert read_headers(path) == ["ColA", "ColB"]

    def test_read_headers_normal(self, tmp_path):
        path = os.path.join(tmp_path, "d.xlsx")
        _make_xlsx([["ColA", "ColB"], ["x", "y"]], path)
        assert read_headers(path) == ["ColA", "ColB"]


class TestWriteReadRoundtrip:
    def test_roundtrip(self, tmp_path):
        path = os.path.join(tmp_path, "r.xlsx")
        headers = ["A", "B"]
        data = [[1, "x"], [2, "y"]]
        write_table(path, headers, data)
        h, rows = read_table(path)
        assert h == headers
        assert len(rows) == 2
