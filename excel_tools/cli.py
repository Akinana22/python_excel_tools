"""交互式主菜单"""

import os
import sys

from .menu_utils import (
    clear_screen, print_header, print_step,
    get_input, get_input_allow_empty, select_from_list,
    BACK, TO_MAIN, VIEW,
)
from .file_browser import browse_files
from .excel_io import read_headers
from .row_filter import (
    filter_rows,
    CATEGORIES, CATEGORY_ORDER,
    NUMBER_OPERATORS, TIME_OPERATORS, CONTENT_OPERATORS,
    OPERATOR_LABELS,
)
from .table_splitter import split_by_column
from .format_converter import convert_to_csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORY_SHORT = {"number": "数值", "time": "时间", "content": "内容"}


def _show_conditions(conditions):
    """显示已有条件，并支持按序号删除。"""
    while True:
        clear_screen()
        print_header("已有条件")
        if not conditions:
            print("  (暂无已有条件)")
        else:
            for i, (col, category, op, val) in enumerate(conditions, 1):
                cat = CATEGORY_SHORT[category]
                op_label = OPERATOR_LABELS[op]
                if op in ("is_null", "not_null"):
                    print(f"  {i}. {col} {cat} {op_label}")
                else:
                    print(f"  {i}. {col} {cat} {op_label} {val}")
        print()
        print("  [0] 返回")
        raw = input("\n  输入序号删除条件 (输入编号, [0]返回): ").strip()
        if raw == "0":
            return
        if raw.isdigit() and 1 <= int(raw) <= len(conditions):
            del conditions[int(raw) - 1]
            print("  已删除该条件")
        else:
            print("  请输入有效编号")


def _select_column(headers, conditions=None):
    """列出所有列名让用户选编号。返回列名 / BACK / TO_MAIN。"""
    allow_view = conditions is not None
    while True:
        clear_screen()
        print_header("选择列")
        result = select_from_list(headers, "请选择列", allow_view=allow_view)
        if result == VIEW:
            _show_conditions(conditions)
            continue
        if result == BACK or result == TO_MAIN:
            return result
        return headers[result]


def _select_operator(category, conditions):
    """按类别选择操作符。返回操作符 / BACK / TO_MAIN。"""
    if category == "number":
        ops = NUMBER_OPERATORS
    elif category == "time":
        ops = TIME_OPERATORS
    else:
        ops = CONTENT_OPERATORS
    labels = [OPERATOR_LABELS[op] for op in ops]
    while True:
        clear_screen()
        print_header(f"选择操作符 ({CATEGORIES[category]})")
        result = select_from_list(labels, "请选择操作符", allow_view=True)
        if result == VIEW:
            _show_conditions(conditions)
            continue
        if result == BACK or result == TO_MAIN:
            return result
        return ops[result]


def _input_value(category, op, conditions):
    """按类别和操作符输入值。返回输入值 / BACK / TO_MAIN。"""
    if op in ("is_null", "not_null"):
        return ""
    while True:
        if category == "time":
            val = get_input("请输入时间值 (如 2024-01-15 17:00:00)", allow_view=True)
        else:
            val = get_input("请输入比较值", allow_view=True)
        if val == VIEW:
            _show_conditions(conditions)
            continue
        return val


def _collect_conditions(headers):
    """收集条件列表。返回 conditions 列表 / BACK / TO_MAIN。"""
    conditions = []

    while True:
        col = _select_column(headers, conditions)
        if col == TO_MAIN:
            return TO_MAIN
        if col == BACK:
            if conditions:
                return conditions
            return BACK

        while True:
            while True:
                cat_idx = select_from_list(
                    [CATEGORIES[c] for c in CATEGORY_ORDER], "请选择比较对象",
                    allow_view=True,
                )
                if cat_idx == VIEW:
                    _show_conditions(conditions)
                    continue
                break
            if cat_idx == TO_MAIN:
                return TO_MAIN
            if cat_idx == BACK:
                break
            category = CATEGORY_ORDER[cat_idx]

            while True:
                op = _select_operator(category, conditions)
                if op == TO_MAIN:
                    return TO_MAIN
                if op == BACK:
                    break

                val = _input_value(category, op, conditions)
                if val == TO_MAIN:
                    return TO_MAIN
                if val == BACK:
                    continue

                conditions.append((col, category, op, val))

                more = input("  继续添加条件? (y/n, [q]主菜单): ").strip().lower()
                if more == "q":
                    return TO_MAIN
                if more == "y":
                    continue
                return conditions


def _select_mode(action, conditions):
    """选择模式。返回 "any"/"all" / BACK / TO_MAIN。"""
    if action == "delete":
        modes = ["任意条件满足→删除", "全部条件满足→删除"]
    else:
        modes = ["任意条件满足→保留", "全部条件满足→保留"]
    while True:
        clear_screen()
        print_header("选择模式")
        result = select_from_list(modes, "请选择模式", allow_view=True)
        if result == VIEW:
            _show_conditions(conditions)
            continue
        if result == BACK or result == TO_MAIN:
            return result
        return "any" if result == 0 else "all"


def _unique_path(path):
    """若路径已存在，累加 (1)(2)... 直到不重名。"""
    if not os.path.exists(path):
        return path
    dir_name = os.path.dirname(path)
    base = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(os.path.basename(path))[1]
    i = 1
    while True:
        candidate = os.path.join(dir_name, f"{base}({i}){ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def _choose_output_format(file_path):
    """选择输出格式。返回 "xlsx"/"csv" / BACK / TO_MAIN。"""
    src_ext = os.path.splitext(file_path)[1].lower()
    if src_ext == ".csv":
        return "csv"
    result = select_from_list(["xlsx", "csv"], "请选择输出格式")
    if result == BACK or result == TO_MAIN:
        return result
    return "xlsx" if result == 0 else "csv"


def _get_filter_output_path(file_path):
    """保留/删除的输出路径设置。返回路径 / BACK / TO_MAIN。"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    dir_name = os.path.dirname(file_path)

    fmt = _choose_output_format(file_path)
    if fmt == BACK or fmt == TO_MAIN:
        return fmt

    name = get_input_allow_empty(
        f"请输入输出文件名 (留空使用默认 result({base_name}))"
    )
    if name == BACK or name == TO_MAIN:
        return name

    name = name.strip()
    if name == "":
        name = f"result({base_name})"
    if not name.lower().endswith("." + fmt):
        name += "." + fmt

    return _unique_path(os.path.join(dir_name, name))


def _execute_filter(file_path, output_path, conditions, mode, action):
    clear_screen()
    print_header("执行中")
    try:
        original, kept = filter_rows(file_path, output_path, conditions, mode, action)
        removed = original - kept
        print("\n  ✅ 处理完成！")
        print(f"  原始行数: {original}")
        print(f"  保留行数: {kept}")
        print(f"  删除行数: {removed}")
        print(f"  输出文件: {output_path}")
    except Exception as e:
        print(f"\n  ❌ 处理失败: {e}")


def _menu_filter(action):
    """保留/删除指定行流程。action: "keep" | "delete"。"""
    title = "保留指定行" if action == "keep" else "删除指定行"

    while True:
        clear_screen()
        print_header(title)
        print_step("步骤 1: 选择要处理的表格文件")
        file_path = browse_files(PROJECT_ROOT)
        if file_path in (BACK, TO_MAIN):
            return
        print(f"\n  已选择: {file_path}")

        headers = read_headers(file_path)

        while True:
            conditions = _collect_conditions(headers)
            if conditions == TO_MAIN:
                return
            if conditions == BACK:
                break
            if not conditions:
                print("\n  未添加任何条件")
                input("  按回车继续...")
                continue

            while True:
                mode = _select_mode(action, conditions)
                if mode == TO_MAIN:
                    return
                if mode == BACK:
                    break

                output_path = _get_filter_output_path(file_path)
                if output_path == TO_MAIN:
                    return
                if output_path == BACK:
                    continue

                _execute_filter(file_path, output_path, conditions, mode, action)
                input("\n  按回车返回主菜单...")
                return


def _menu_split():
    """表格拆分流程。"""
    while True:
        clear_screen()
        print_header("表格拆分")
        print_step("步骤 1: 选择要拆分的表格文件")
        file_path = browse_files(PROJECT_ROOT)
        if file_path in (BACK, TO_MAIN):
            return
        print(f"\n  已选择: {file_path}")

        headers = read_headers(file_path)
        col = _select_column(headers)
        if col == TO_MAIN:
            return
        if col == BACK:
            continue

        rows_input = get_input_allow_empty("输入每子表行数 (不拆分则输入 0 或直接回车)")
        if rows_input == TO_MAIN:
            return
        if rows_input == BACK:
            continue
        rows_per_file = None
        if rows_input.strip().isdigit() and int(rows_input.strip()) > 0:
            rows_per_file = int(rows_input.strip())

        fmt = _choose_output_format(file_path)
        if fmt == TO_MAIN:
            return
        if fmt == BACK:
            continue

        clear_screen()
        print_header("表格拆分 - 执行中")
        try:
            files = split_by_column(file_path, col, rows_per_file, fmt)
            print(f"\n  ✅ 拆分完成！共生成 {len(files)} 个文件:")
            for f in files:
                print(f"    · {os.path.basename(f)}")
        except Exception as e:
            print(f"\n  ❌ 处理失败: {e}")

        input("\n  按回车返回主菜单...")
        return


def _menu_convert():
    """格式转换流程。"""
    while True:
        clear_screen()
        print_header("格式转换 (→ CSV)")
        print_step("步骤 1: 选择要转换的表格文件")
        file_path = browse_files(PROJECT_ROOT)
        if file_path in (BACK, TO_MAIN):
            return
        print(f"\n  已选择: {file_path}")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        dir_name = os.path.dirname(file_path)
        name = get_input_allow_empty(f"请输入输出文件名 (留空使用默认 {base_name}.csv)")
        if name == TO_MAIN:
            return
        if name == BACK:
            continue

        name = name.strip()
        if name == "":
            name = f"{base_name}.csv"
        elif not name.lower().endswith(".csv"):
            name += ".csv"
        output_path = _unique_path(os.path.join(dir_name, name))

        clear_screen()
        print_header("格式转换 - 执行中")
        try:
            result = convert_to_csv(file_path, output_path)
            print(f"\n  ✅ 转换完成！")
            print(f"  输出文件: {result}")
        except Exception as e:
            print(f"\n  ❌ 转换失败: {e}")

        input("\n  按回车返回主菜单...")
        return


def _show_main_menu():
    clear_screen()
    print_header("Python 表格文件处理工具", width=40)
    print("  [1] 保留指定行")
    print("  [2] 删除指定行")
    print("  [3] 表格拆分")
    print("  [4] 格式转换 (→ CSV)")
    print("  [0] 退出程序")
    print()


def main():
    while True:
        _show_main_menu()
        choice = input("  请选择功能 (输入编号): ").strip()

        if choice == "0":
            print("\n  已退出程序")
            sys.exit(0)
        elif choice == "1":
            _menu_filter("keep")
        elif choice == "2":
            _menu_filter("delete")
        elif choice == "3":
            _menu_split()
        elif choice == "4":
            _menu_convert()
        else:
            print("  请输入有效编号 (0~4)")
            input("  按回车继续...")


if __name__ == "__main__":
    main()
