"""文件浏览器：支持子目录浏览的交互式表格文件选择器"""

import os
import sys
from .menu_utils import clear_screen, print_header

TABLE_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def _is_table_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in TABLE_EXTENSIONS


def browse_files(start_dir):
    """交互式文件浏览器。

    Args:
        start_dir: 起始浏览目录

    Returns:
        选中的文件完整路径，None 表示用户取消选择
    """
    current_dir = os.path.abspath(start_dir)

    while True:
        clear_screen()
        print_header("文件浏览器")
        print(f"  当前目录: {current_dir}")
        print()

        try:
            entries = sorted(os.listdir(current_dir))
        except PermissionError:
            print("  [错误] 无权限访问该目录")
            if _go_parent(current_dir) != current_dir:
                current_dir = _go_parent(current_dir)
                continue
            input("\n  按回车返回上级...")
            return None

        dirs = []
        files = []
        for entry in entries:
            full = os.path.join(current_dir, entry)
            if os.path.isdir(full):
                dirs.append(entry)
            elif os.path.isfile(full) and _is_table_file(entry):
                files.append(entry)

        idx = 1
        mapping = {}

        if _go_parent(current_dir) != current_dir:
            print(f"  [{idx}] [目录] .. (上级目录)")
            mapping[idx] = ".."
            idx += 1

        for d in dirs:
            print(f"  [{idx}] [目录] {d}/")
            mapping[idx] = d
            idx += 1

        for f in files:
            prefix = "📊 " if f.endswith(".xlsx") or f.endswith(".xls") else "📄 "
            print(f"  [{idx}] {prefix}{f}")
            mapping[idx] = f
            idx += 1

        print(f"  [0] 返回上级菜单")

        if idx == 1:
            print("\n  (该目录下没有表格文件)")

        raw = input(f"\n  请选择 (输入编号, [0]返回, [q]退出): ").strip()
        if raw.lower() == "q":
            print("\n已退出程序")
            sys.exit(0)
        if raw == "0":
            return None
        if not raw.isdigit():
            print("  请输入有效编号")
            input("  按回车继续...")
            continue

        num = int(raw)
        if num not in mapping:
            print("  请输入有效编号")
            input("  按回车继续...")
            continue

        selected = mapping[num]
        if selected == "..":
            current_dir = _go_parent(current_dir)
            continue

        target_path = os.path.join(current_dir, selected)
        if os.path.isdir(target_path):
            current_dir = target_path
            continue

        confirmed = input(f"\n  已选择: {target_path}\n  确认? (y/n, [0]返回, [q]退出): ").strip().lower()
        if confirmed == "q":
            print("\n已退出程序")
            sys.exit(0)
        if confirmed == "0":
            continue
        if confirmed == "y" or confirmed == "yes":
            return target_path


def _go_parent(path):
    parent = os.path.dirname(path)
    if parent == path:
        return path
    return parent
