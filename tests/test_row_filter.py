"""测试条件删除行"""

import os
import sys
import openpyxl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from excel_tools.excel_io import read_table
from excel_tools.row_filter import filter_rows, _check_condition


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
    def test_eq(self):
        assert _check_condition("NY", "==", "NY") is True
        assert _check_condition("LA", "==", "NY") is False

    def test_neq(self):
        assert _check_condition("LA", "!=", "NY") is True
        assert _check_condition("NY", "!=", "NY") is False

    def test_gt(self):
        assert _check_condition(30, ">", "25") is True
        assert _check_condition(17, ">", "25") is False

    def test_lt(self):
        assert _check_condition(17, "<", "25") is True
        assert _check_condition(30, "<", "25") is False

    def test_gte(self):
        assert _check_condition(25, ">=", "25") is True

    def test_lte(self):
        assert _check_condition(25, "<=", "25") is True

    def test_contains(self):
        assert _check_condition("Alice", "contains", "li") is True
        assert _check_condition("Bob", "contains", "li") is False

    def test_not_contains(self):
        assert _check_condition("Bob", "not_contains", "li") is True
        assert _check_condition("Alice", "not_contains", "li") is False

    def test_is_null(self):
        assert _check_condition(None, "is_null", "") is True
        assert _check_condition("", "is_null", "") is True
        assert _check_condition("NY", "is_null", "") is False

    def test_not_null(self):
        assert _check_condition("NY", "not_null", "") is True
        assert _check_condition(None, "not_null", "") is False

    def test_eq_numeric_float(self):
        assert _check_condition(25.0, "==", "25") is True
        assert _check_condition(25.5, "==", "25") is False


class TestFilterRows:
    def test_any_mode_delete_if_any_satisfies(self, sample_xlsx):
        """任意条件满足即删除。只有 Diana(None,60) age 为空不满足<18，其余都满足至少一个。"""
        out = os.path.join(os.path.dirname(sample_xlsx), "out_any.xlsx")
        orig, deleted = filter_rows(
            sample_xlsx, out,
            [("Age", "<", "18"), ("Score", "<", "60")],
            delete_mode="any",
        )
        assert orig == 5
        assert deleted == 3  # Bob(17<18), Diana(None→""<"18"), ""(55<60)

    def test_all_mode_delete_if_all_satisfy(self, sample_xlsx):
        """全部条件满足才删除。Alice 和 Charlie 年龄>=25 且 City=NY。"""
        out = os.path.join(os.path.dirname(sample_xlsx), "out_all.xlsx")
        orig, deleted = filter_rows(
            sample_xlsx, out,
            [("Age", ">=", "25"), ("City", "==", "NY")],
            delete_mode="all",
        )
        assert orig == 5
        assert deleted == 2  # Alice(25,NY), Charlie(30,NY)

    def test_output_columns_preserved(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out_cols.xlsx")
        filter_rows(sample_xlsx, out, [("Age", "<", "1")], delete_mode="any")
        h, _ = read_table(out)
        assert h == HEADERS

    def test_csv_output(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out.csv")
        filter_rows(sample_xlsx, out, [("Age", "<", "1")], delete_mode="any")
        assert os.path.exists(out)

    def test_column_not_found(self, sample_xlsx):
        out = os.path.join(os.path.dirname(sample_xlsx), "out_err.xlsx")
        with pytest.raises(ValueError, match="不存在"):
            filter_rows(sample_xlsx, out, [("Unknown", ">", "1")], delete_mode="any")
