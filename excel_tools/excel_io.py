"""统一表格读写模块：支持 .xlsx / .xls / .csv 三种格式"""

import csv
import os
import openpyxl


def read_table(file_path):
    """读取表格文件，返回 (表头列表, 数据行列表)。

    数据行每行为一个 list，None 表示空单元格。
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return [], []
        headers = rows[0]
        data = rows[1:]
        return headers, data

    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        headers = [ws.cell_value(0, c) for c in range(ws.ncols)]
        data = []
        for r in range(1, ws.nrows):
            row = [ws.cell_value(r, c) if ws.cell_value(r, c) != "" else None for c in range(ws.ncols)]
            data.append(row)
        return headers, data

    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]
    wb.close()
    return headers, data


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
