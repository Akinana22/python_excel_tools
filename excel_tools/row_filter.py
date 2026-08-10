"""条件删除行"""

from .excel_io import read_table, write_table

OPERATORS = {
    "==": "等于",
    "!=": "不等于",
    ">": "大于",
    "<": "小于",
    ">=": "大于等于",
    "<=": "小于等于",
    "contains": "包含",
    "not_contains": "不包含",
    "is_null": "为空",
    "not_null": "不为空",
}

OP_DISPLAY_ORDER = ["==", "!=", ">", "<", ">=", "<=", "contains", "not_contains", "is_null", "not_null"]


def _try_numeric(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _check_condition(cell_value, op, val):
    """检查单个单元格是否满足条件。返回 True 表示满足。"""
    if op == "is_null":
        return cell_value is None or (isinstance(cell_value, str) and cell_value == "")
    if op == "not_null":
        return cell_value is not None and not (isinstance(cell_value, str) and cell_value == "")

    cell_str = str(cell_value) if cell_value is not None else ""

    if op in ("contains", "not_contains"):
        result = val in cell_str
        return not result if op == "not_contains" else result

    num_cell = _try_numeric(cell_value)
    num_val = _try_numeric(val)

    if num_cell is not None and num_val is not None:
        if op == "==":
            return num_cell == num_val
        elif op == "!=":
            return num_cell != num_val
        elif op == ">":
            return num_cell > num_val
        elif op == "<":
            return num_cell < num_val
        elif op == ">=":
            return num_cell >= num_val
        elif op == "<=":
            return num_cell <= num_val

    if op == "==":
        return cell_str == val
    elif op == "!=":
        return cell_str != val
    elif op == ">":
        return cell_str > val
    elif op == "<":
        return cell_str < val
    elif op == ">=":
        return cell_str >= val
    elif op == "<=":
        return cell_str <= val

    raise ValueError(f"不支持的操作符: {op}")


def filter_rows(
    file_path,
    output_path,
    conditions,  # [(列名, 操作符, 值), ...]
    delete_mode,  # "any" 任意条件满足即删, "all" 全部条件满足才删
):
    """条件删除行。

    Args:
        file_path: 源文件路径
        output_path: 输出文件路径
        conditions: 条件列表，每个元素为 (列名, 操作符, 值)
         delete_mode: "any"(任意条件满足即删) | "all"(全部条件满足才删)

    Returns:
        (原始行数, 删除行数)
    """
    headers, rows = read_table(file_path)

    original_rows = len(rows)

    if not conditions:
        raise ValueError("至少需要指定一个条件")

    col_indices = []
    for col, op, val in conditions:
        if col not in headers:
            raise ValueError(f"列 '{col}' 不存在于表格中。可用列: {headers}")
        col_indices.append((headers.index(col), op, val))

    kept = []
    for row in rows:
        results = []
        for col_idx, op, val in col_indices:
            cell_value = row[col_idx] if col_idx < len(row) else None
            results.append(_check_condition(cell_value, op, val))

        if delete_mode == "any":
            should_delete = any(results)
        elif delete_mode == "all":
            should_delete = all(results)
        else:
            raise ValueError(f"不支持的删除模式: {delete_mode}，应为 'any' 或 'all'")

        if not should_delete:
            kept.append(row)

    deleted_rows = original_rows - len(kept)
    write_table(output_path, headers, kept)
    return original_rows, deleted_rows
