"""表格拆分：按列分类拆分 + 按行数拆分"""

import math
import os

from .excel_io import read_table, write_table


def _get_base_and_ext(file_path) :
    """返回 (目录, 基础名(不含扩展名), 扩展名)。"""
    dir_name = os.path.dirname(file_path)
    base = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(os.path.basename(file_path))[1].lower()
    if ext not in (".xlsx", ".xls", ".csv"):
        ext = ".xlsx"
    elif ext == ".xls":
        ext = ".xlsx"
    return dir_name, base, ext


def _split_file_by_count(file_path, rows_per_file)     :
    """对单个文件按行数拆分。返回生成的子文件路径列表。"""
    headers, rows = read_table(file_path)
    total_rows = len(rows)
    total_files = math.ceil(total_rows / rows_per_file)
    pad_width = max(2, len(str(total_files)))

    dir_name, base, ext = _get_base_and_ext(file_path)
    generated = []

    for i in range(total_files):
        start = i * rows_per_file
        end = min(start + rows_per_file, total_rows)
        chunk = rows[start:end]
        num_str = str(i + 1).zfill(pad_width)
        out_name = f"{base}-{num_str}{ext}"
        out_path = os.path.join(dir_name, out_name)
        write_table(out_path, headers, chunk)
        generated.append(out_path)

    return generated


def split_by_column(
    file_path,
    column,
    rows_per_file = None,
)     :
    """按指定列拆分表格，可选二级按行数拆分。

    Args:
        file_path: 源文件路径
        column: 作为分类依据的列名
        rows_per_file: 二级拆分每文件行数，None 则仅按列拆分

    Returns:
        生成的所有文件路径列表（不含原始文件）
    """
    headers, rows = read_table(file_path)

    if column not in headers:
        raise ValueError(f"列 '{column}' 不存在于表格中。可用列: {headers}")

    col_idx = headers.index(column)

    # 按列值分组
    groups = {}
    null_rows = []

    for row in rows:
        col_val = row[col_idx] if col_idx < len(row) else None
        if col_val is None or (isinstance(col_val, str) and col_val == ""):
            null_rows.append(row)
        else:
            key = str(col_val)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

    if null_rows:
        groups["(空值)"] = null_rows

    dir_name, base, ext = _get_base_and_ext(file_path)
    output_dir = os.path.join(dir_name, base)
    os.makedirs(output_dir, exist_ok=True)
    all_files = []

    for key in sorted(groups.keys()):
        safe_val = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        out_name = f"{base}-{safe_val}{ext}"
        out_path = os.path.join(output_dir, out_name)
        write_table(out_path, headers, groups[key])
        all_files.append(out_path)

        if rows_per_file is not None and rows_per_file > 0 and len(groups[key]) > rows_per_file:
            sub_files = _split_file_by_count(out_path, rows_per_file)
            all_files.extend(sub_files)

    return all_files
