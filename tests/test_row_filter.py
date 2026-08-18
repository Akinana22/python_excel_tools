"""测试条件删除/保留行"""

import os
import sys
from datetime import datetime
import openpyxl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from excel_tools.excel_io import read_table
from excel_tools.row_filter import filter_rows, _check_condition, _try_date


HEADERS = ["Name", "Age", "Score", "City"]
ROWS = [
    ["Alice", 25, 88, "NY"],
    ["Bob", 17, 92, "LA"],
    ["Charlie", 30, 75, "NY"],
    ["Diana", None, 60, "LA"],
    ["", 40, 55, "SF"],
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
    path = os.path.join(tmp_path, "test.xlsx")
    _make_xlsx(HEADERS, ROWS, path)
    return path


class TestCheckCondition:
    def test_number_gt(self):
        assert _check_condition(30, "number", ">", "25") is True
        assert _check_condition(17, "number", ">", "25") is False

    def test_number_eq(self):
        assert _check_condition(25, "number", "==", "25") is True

    def test_number_lt(self):
        assert _check_condition(17, "number", "<", "25") is True

    def test_content_contains(self):
        assert _check_condition("Alice", "content", "contains", "li") is True
        assert _check_condition("Bob", "content", "contains", "li") is False

    def test_content_not_contains(self):
        assert _check_condition("Bob", "content", "not_contains", "li") is True

    def test_content_is_null(self):
        assert _check_condition(None, "content", "is_null", "") is True
        assert _check_condition("", "content", "is_null", "") is True
        assert _check_condition("NY", "content", "is_null", "") is False

    def test_content_not_null(self):
        assert _check_condition("NY", "content", "not_null", "") is True
        assert _check_condition(None, "content", "not_null", "") is False

    def test_time_gt(self):
        assert _check_condition("2024-01-15 17:00:00", "time", ">", "2024-01-15 00:00:00") is True
        assert _check_condition("2024-01-15 00:00:00", "time", ">", "2024-01-15 17:00:00") is False

    def test_time_eq_datetime_object(self):
        cell = datetime(2024, 1, 15, 17, 0, 0)
        assert _check_condition(cell, "time", "==", "2024-01-15 17:00:00") is True

    def test_time_unparseable(self):
        assert _check_condition("abc", "time", ">", "2024-01-15") is False


class TestTryDate:
    def test_dash_with_time(self):
        assert _try_date("2024-01-15 17:00:00") == datetime(2024, 1, 15, 17, 0, 0)

    def test_slash_no_padding(self):
        assert _try_date("2024/1/15 0:00:00") == datetime(2024, 1, 15, 0, 0, 0)

    def test_no_seconds(self):
        assert _try_date("2024-01-15 13:02") == datetime(2024, 1, 15, 13, 2)

    def test_leading_apostrophe(self):
        assert _try_date("'2001-10-08 00:00:00") == datetime(2001, 10, 8, 0, 0, 0)

    def test_compact(self):
        assert _try_date("20220426") == datetime(2022, 4, 26)

    def test_chinese(self):
        assert _try_date("2024年5月22日") == datetime(2024, 5, 22)

    def test_date_only(self):
        assert _try_date("2024-01-15") == datetime(2024, 1, 15)

    def test_invalid(self):
        assert _try_date("not-a-date") is None


class TestFilterRows:
    def test_delete_any(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.xlsx")
        original, kept = filter_rows(
            sample_xlsx, out,
            [("Age", "number", "<", "18"), ("Score", "number", "<", "60")],
            mode="any", action="delete",
        )
        assert original == 5
        assert kept == 2

    def test_delete_all(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.xlsx")
        original, kept = filter_rows(
            sample_xlsx, out,
            [("Age", "number", ">=", "25"), ("City", "number", "==", "NY")],
            mode="all", action="delete",
        )
        assert original == 5
        assert kept == 3

    def test_keep_any(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.xlsx")
        original, kept = filter_rows(
            sample_xlsx, out,
            [("Age", "number", "<", "18"), ("Score", "number", "<", "60")],
            mode="any", action="keep",
        )
        assert original == 5
        assert kept == 3

    def test_keep_all(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.xlsx")
        original, kept = filter_rows(
            sample_xlsx, out,
            [("Age", "number", ">=", "25"), ("City", "number", "==", "NY")],
            mode="all", action="keep",
        )
        assert original == 5
        assert kept == 2

    def test_csv_output(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.csv")
        original, kept = filter_rows(
            sample_xlsx, out,
            [("Age", "number", "<", "1")],
            mode="any", action="delete",
        )
        assert os.path.exists(out)

    def test_column_not_found(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.xlsx")
        with pytest.raises(ValueError, match="不存在"):
            filter_rows(sample_xlsx, out, [("Unknown", "number", ">", "1")], "any", "delete")

    def test_time_filter(self, tmp_path):
        h = ["Name", "Time"]
        r = [
            ["a", "2024-01-15 17:00:00"],
            ["b", "2024-01-16 00:00:00"],
            ["c", "2024-01-14 00:00:00"],
        ]
        p = os.path.join(tmp_path, "t.xlsx")
        _make_xlsx(h, r, p)
        out = os.path.join(tmp_path, "t_out.xlsx")
        original, kept = filter_rows(
            p, out,
            [("Time", "time", ">", "2024-01-15 00:00:00")],
            mode="any", action="delete",
        )
        assert original == 3
        assert kept == 1
