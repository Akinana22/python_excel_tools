"""测试表格拆分"""

import os
import sys
import openpyxl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from excel_tools.excel_io import read_table
from excel_tools.table_splitter import split_by_column


HEADERS = ["Name", "Category", "Score"]
ROWS = [
    ["Alice", "A", 88],
    ["Bob", "B", 92],
    ["Charlie", "A", 75],
    ["Diana", "B", 60],
    ["Eve", "A", 55],
    ["Frank", None, 80],
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
    path = os.path.join(tmp_path, "test_split.xlsx")
    _make_xlsx(HEADERS, ROWS, path)
    return path


class TestSplitByColumn:
    def test_output_in_subfolder(self, sample_xlsx):
        """输出应在以原文件名命名的文件夹下。"""
        files = split_by_column(sample_xlsx, "Category")
        expected_dir = os.path.join(os.path.dirname(sample_xlsx), "test_split")
        assert len(files) == 3
        for f in files:
            assert os.path.dirname(f) == expected_dir

    def test_split_count(self, sample_xlsx):
        files = split_by_column(sample_xlsx, "Category")
        assert len(files) == 3

    def test_category_a_rows(self, sample_xlsx):
        files = split_by_column(sample_xlsx, "Category")
        a_file = [f for f in files if "A.xlsx" in f][0]
        _, rows = read_table(a_file)
        assert len(rows) == 3

    def test_category_b_rows(self, sample_xlsx):
        files = split_by_column(sample_xlsx, "Category")
        b_file = [f for f in files if "B.xlsx" in f][0]
        _, rows = read_table(b_file)
        assert len(rows) == 2

    def test_null_rows(self, sample_xlsx):
        files = split_by_column(sample_xlsx, "Category")
        null_file = [f for f in files if "(空值)" in f][0]
        _, rows = read_table(null_file)
        assert len(rows) == 1

    def test_with_row_split_sub_files(self, sample_xlsx):
        files = split_by_column(sample_xlsx, "Category", rows_per_file=2)
        assert len(files) == 5

    def test_column_not_found(self, sample_xlsx):
        with pytest.raises(ValueError, match="不存在"):
            split_by_column(sample_xlsx, "Unknown")

    def test_csv_input(self, tmp_path):
        import csv
        csv_path = os.path.join(tmp_path, "test.csv")
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEADERS)
            w.writerows(ROWS)
        files = split_by_column(csv_path, "Category")
        assert len(files) == 3
