"""统一表格读写模块：支持 .xlsx / .xls / .csv 三种格式"""

import csv
import os
import openpyxl


def _nonempty_count(row):
    if row is None:
        return 0
    return sum(1 for v in row if v is not None and str(v).strip() != "")


def _detect_title_offset(rows):
    """检测标题行偏移：首行仅一个非空单元格、次行多个非空，则首行为标题。"""
    if len(rows) < 2:
        return 0
    if _nonempty_count(rows[0]) <= 1 and _nonempty_count(rows[1]) >= 2:
        return 1
    return 0


def _read_all_rows(file_path):
    """读取所有行（不做表头假设），返回行列表。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            return list(csv.reader(f))

    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        rows = []
        for r in range(ws.nrows):
            row = []
            for c in range(ws.ncols):
                cell = ws.cell(r, c)
                if cell.ctype == xlrd.XL_CELL_DATE:
                    row.append(xlrd.xldate_as_datetime(cell.value, wb.datemode))
                else:
                    v = cell.value
                    row.append(None if v == "" else v)
            rows.append(row)
        return rows

    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    rows = [list(row) for row in ws.iter_rows(values_only=True)]
    wb.close()
    return rows


def read_table(file_path):
    """读取表格，返回 (表头列表, 数据行列表)。自动跳过标题行。"""
    all_rows = _read_all_rows(file_path)
    if not all_rows:
        return [], []
    offset = _detect_title_offset(all_rows)
    headers = all_rows[offset]
    rows = all_rows[offset + 1:]
    return headers, rows


def read_headers(file_path):
    """只读取表头（含标题检测），返回列名列表。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            first = next(reader, None)
            second = next(reader, None)
        sample = [first] if second is None else [first, second]
        offset = _detect_title_offset(sample)
        return sample[offset] if sample and sample[offset] is not None else []

    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        if ws.nrows >= 2:
            rows = [ws.row_values(0), ws.row_values(1)]
        else:
            rows = [ws.row_values(0)]
        offset = _detect_title_offset(rows)
        return list(rows[offset]) if rows else []

    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    rows = [list(row) for row in ws.iter_rows(min_row=1, max_row=2, values_only=True)]
    wb.close()
    offset = _detect_title_offset(rows)
    return rows[offset] if offset < len(rows) else []


def write_table(file_path, headers, data):
    """将表头和数据行写入表格文件，根据扩展名自动判断格式。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        return

    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()
    ws.append(headers)
    for row in data:
        ws.append(row)
    wb.save(file_path)
    wb.close()
