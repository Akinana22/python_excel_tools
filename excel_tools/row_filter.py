"""条件删除/保留行"""

from datetime import datetime, date

from .excel_io import read_table, write_table

CATEGORIES = {
    "number": "数值条件",
    "time": "时间条件",
    "content": "内容条件",
}

CATEGORY_ORDER = ["number", "time", "content"]

NUMBER_OPERATORS = [">", "<", ">=", "<=", "==", "!="]
TIME_OPERATORS = [">", "<", ">=", "<=", "==", "!="]
CONTENT_OPERATORS = ["contains", "not_contains", "is_null", "not_null"]

OPERATOR_LABELS = {
    ">": "大于",
    "<": "小于",
    ">=": "大于等于",
    "<=": "小于等于",
    "==": "等于",
    "!=": "不等于",
    "contains": "包含",
    "not_contains": "不包含",
    "is_null": "为空",
    "not_null": "不为空",
}

DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%Y%m%d",
    "%Y年%m月%d日",
    "%Y年%m月%d日 %H:%M:%S",
    "%Y年%m月%d日 %H:%M",
]


def _try_numeric(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _try_date(val):
    """将值解析为 datetime，失败返回 None。支持多种格式，剥离前导单引号。"""
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day)
    if val is None:
        return None
    s = str(val).strip()
    if s.startswith("'"):
        s = s[1:].strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _compare(a, b, op):
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == ">":
        return a > b
    if op == "<":
        return a < b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    raise ValueError(f"不支持的操作符: {op}")


def _check_content(cell_value, op, val):
    cell_str = str(cell_value) if cell_value is not None else ""
    if op == "is_null":
        return cell_value is None or cell_str == ""
    if op == "not_null":
        return not (cell_value is None or cell_str == "")
    if op == "contains":
        return val in cell_str
    if op == "not_contains":
        return val not in cell_str
    raise ValueError(f"不支持的内容操作符: {op}")


def _check_number(cell_value, op, val):
    num_cell = _try_numeric(cell_value)
    num_val = _try_numeric(val)
    if num_cell is not None and num_val is not None:
        return _compare(num_cell, num_val, op)
    cell_str = str(cell_value) if cell_value is not None else ""
    return _compare(cell_str, val, op)


def _check_condition(cell_value, category, op, val):
    """检查单个单元格是否满足条件。返回 True 表示满足。

    category: "number" | "time" | "content"
    """
    if category == "content":
        return _check_content(cell_value, op, val)
    if category == "time":
        date_cell = _try_date(cell_value)
        date_val = _try_date(val)
        if date_cell is None or date_val is None:
            return False
        return _compare(date_cell, date_val, op)
    if category == "number":
        return _check_number(cell_value, op, val)
    raise ValueError(f"不支持的条件类别: {category}")


def filter_rows(file_path, output_path, conditions, mode, action):
    """删除或保留满足条件的行。

    Args:
        file_path: 源文件路径
        output_path: 输出文件路径
        conditions: 条件列表，每个元素为 (列名, 类别, 操作符, 值)
        mode: "any" | "all"
        action: "keep"(保留满足条件) | "delete"(删除满足条件)

    Returns:
        (原始行数, 保留行数)
    """
    headers, rows = read_table(file_path)
    original_rows = len(rows)

    if not conditions:
        raise ValueError("至少需要指定一个条件")

    col_indices = []
    for col, category, op, val in conditions:
        if col not in headers:
            raise ValueError(f"列 '{col}' 不存在于表格中。可用列: {headers}")
        col_indices.append((headers.index(col), category, op, val))

    kept = []
    for row in rows:
        results = []
        for col_idx, category, op, val in col_indices:
            cell_value = row[col_idx] if col_idx < len(row) else None
            results.append(_check_condition(cell_value, category, op, val))

        if mode == "any":
            matched = any(results)
        elif mode == "all":
            matched = all(results)
        else:
            raise ValueError(f"不支持的模式: {mode}，应为 'any' 或 'all'")

        if action == "delete":
            keep = not matched
        elif action == "keep":
            keep = matched
        else:
            raise ValueError(f"不支持的操作: {action}，应为 'keep' 或 'delete'")

        if keep:
            kept.append(row)

    write_table(output_path, headers, kept)
    return original_rows, len(kept)
