"""格式转换：将表格文件转换为 CSV 格式"""

import csv
import os


def convert_to_csv(
    file_path,
    output_path = None,
    encoding = "utf-8-sig",
):
    """将表格文件转换为 CSV。

    支持 .xlsx、.xls、.csv 作为输入，输出为 .csv。

    Args:
        file_path: 源文件路径
        output_path: 输出 CSV 路径，None 则自动生成为同名 .csv
        encoding: 输出编码

    Returns:
        生成的 CSV 文件路径
    """
    if output_path is None:
        dir_name = os.path.dirname(file_path)
        base = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(dir_name, f"{base}.csv")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        # 直接复制，重编码
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f_in:
            reader = csv.reader(f_in)
            rows = list(reader)
        with open(output_path, "w", encoding=encoding, newline="") as f_out:
            writer = csv.writer(f_out)
            writer.writerows(rows)
        return output_path

    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        with open(output_path, "w", encoding=encoding, newline="") as f_out:
            writer = csv.writer(f_out)
            for r in range(ws.nrows):
                row = [ws.cell_value(r, c) for c in range(ws.ncols)]
                writer.writerow(row)
        return output_path

    import openpyxl
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    with open(output_path, "w", encoding=encoding, newline="") as f_out:
        writer = csv.writer(f_out)
        for row in ws.iter_rows(values_only=True):
            writer.writerow(row)
    wb.close()
    return output_path
