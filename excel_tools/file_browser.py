"""文件浏览器：支持子目录浏览的交互式表格文件选择器"""

import os

from .menu_utils import clear_screen, print_header, BACK, TO_MAIN

TABLE_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def _is_table_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in TABLE_EXTENSIONS


def browse_files(start_dir):
    """交互式文件浏览器。

    Args:
        start_dir: 起始浏览目录

    Returns:
        选中的文件完整路径 / BACK / TO_MAIN
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
            input("  按回车返回上级...")
            return BACK

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

        print("  [0] 返回上级")
        print("  [q] 返回主菜单")

        if idx == 1:
            print("\n  (该目录下没有表格文件)")

        raw = input("\n  请选择 (输入编号): ").strip()
        if raw.lower() == "q":
            return TO_MAIN
        if raw == "0":
            return BACK
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

        confirmed = input(f"\n  已选择: {target_path}\n  确认? (y/n, [0]返回, [q]主菜单): ").strip().lower()
        if confirmed == "q":
            return TO_MAIN
        if confirmed == "0":
            continue
        if confirmed in ("y", "yes"):
            return target_path


def _go_parent(path):
    parent = os.path.dirname(path)
    if parent == path:
        return path
    return parent
