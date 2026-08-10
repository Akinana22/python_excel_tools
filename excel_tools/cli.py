"""交互式主菜单"""

import os
import sys

from .menu_utils import clear_screen, print_header, print_step, get_input_or_back, select_from_list
from .file_browser import browse_files
from .row_filter import filter_rows, OPERATORS, OP_DISPLAY_ORDER
from .table_splitter import split_by_column
from .format_converter import convert_to_csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _menu_filter():
    """删除指定行流程。"""
    while True:
        clear_screen()
        print_header("删除指定行")

        print_step("步骤 1: 选择要处理的表格文件")
        file_path = browse_files(PROJECT_ROOT)
        if file_path is None:
            return
        print(f"\n  已选择: {file_path}")

        conditions = []
        while True:
            clear_screen()
            print_header("删除指定行 - 添加条件")
            print(f"  文件: {os.path.basename(file_path)}")
            if conditions:
                print(f"  已添加 {len(conditions)} 条条件:")
                for c, o, v in conditions:
                    print(f"    · {c} {o} {v}")
            print()

            col = get_input_or_back("  输入列名")
            if col is None:
                if conditions:
                    break
                return

            op_list = OP_DISPLAY_ORDER
            op_display = [f"{op} ({OPERATORS[op]})" for op in op_list]
            idx = select_from_list(op_display, "  请选择操作符")
            if idx is None:
                continue
            op = op_list[idx]

            if op in ("is_null", "not_null"):
                val = ""
            else:
                val = get_input_or_back("  输入比较值")
                if val is None:
                    continue

            conditions.append((col, op, val))

            more = get_input_or_back("  继续添加条件? (y/n)")
            if more is None or more.strip().lower() != "y":
                break

        if not conditions:
            print("\n  未添加任何条件，返回主菜单")
            input("  按回车继续...")
            return

        clear_screen()
        print_header("删除指定行 - 删除模式")
        modes = ["任意条件满足→删除", "全部条件满足→删除"]
        mode_idx = select_from_list(modes, "  请选择删除模式")
        if mode_idx is None:
            return
        delete_mode = "any" if mode_idx == 0 else "all"

        output_name = get_input_or_back("  输入输出文件名 (如 result.xlsx)")
        if output_name is None:
            return

        if not output_name.lower().endswith((".xlsx", ".xls", ".csv")):
            output_name += ".xlsx"

        output_path = os.path.join(PROJECT_ROOT, output_name)

        clear_screen()
        print_header("删除指定行 - 执行中")
        try:
            original, deleted = filter_rows(file_path, output_path, conditions, delete_mode)
            print(f"\n  ✅ 处理完成！")
            print(f"  原始行数: {original}")
            print(f"  删除行数: {deleted}")
            print(f"  保留行数: {original - deleted}")
            print(f"  输出文件: {output_path}")
        except Exception as e:
            print(f"\n  ❌ 处理失败: {e}")

        input("\n  按回车返回主菜单...")
        return


def _menu_split():
    """表格拆分流程。"""
    while True:
        clear_screen()
        print_header("表格拆分")

        print_step("步骤 1: 选择要拆分的表格文件")
        file_path = browse_files(PROJECT_ROOT)
        if file_path is None:
            return
        print(f"\n  已选择: {file_path}")

        col = get_input_or_back("  输入作为分类依据的列名")
        if col is None:
            return

        rows_input = get_input_or_back("  输入每子表行数 (不拆分则输入 0 或直接回车)")
        if rows_input is None:
            return

        rows_per_file = None
        if rows_input.strip().isdigit():
            r = int(rows_input.strip())
            if r > 0:
                rows_per_file = r

        clear_screen()
        print_header("表格拆分 - 执行中")
        try:
            files = split_by_column(file_path, col, rows_per_file)
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
        if file_path is None:
            return
        print(f"\n  已选择: {file_path}")

        default_output = os.path.join(
            PROJECT_ROOT,
            os.path.splitext(os.path.basename(file_path))[0] + ".csv"
        )
        output_name = get_input_or_back(
            f"  输入输出文件名 (直接回车使用默认: {os.path.basename(default_output)})"
        )
        if output_name is None:
            return

        if output_name.strip() == "":
            output_path = default_output
        else:
            if not output_name.lower().endswith(".csv"):
                output_name += ".csv"
            output_path = os.path.join(PROJECT_ROOT, output_name)

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
    print("  [1] 删除指定行")
    print("  [2] 表格拆分")
    print("  [3] 格式转换 (→ CSV)")
    print("  [0] 退出程序")
    print()


def main():
    while True:
        _show_main_menu()
        choice = input("  请选择功能 (输入编号): ").strip()

        if choice == "0" or choice.lower() == "q":
            print("\n  已退出程序")
            sys.exit(0)
        elif choice == "1":
            _menu_filter()
        elif choice == "2":
            _menu_split()
        elif choice == "3":
            _menu_convert()
        else:
            print("  请输入有效编号 (0~3)")
            input("  按回车继续...")


if __name__ == "__main__":
    main()
