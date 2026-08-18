"""通用菜单工具：输入获取、清屏、导航处理"""

import os
import sys

BACK = "0"       # 返回上一级菜单
TO_MAIN = "q"    # 返回主菜单


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_input(prompt, allow_back=True, allow_main=True):
    """获取用户输入。

    Returns:
        用户输入字符串 / BACK / TO_MAIN
    """
    hints = []
    if allow_back:
        hints.append("[0]返回")
    if allow_main:
        hints.append("[q]主菜单")
    hint_str = " ".join(hints)
    display = f"{prompt} ({hint_str}): " if hints else f"{prompt}: "

    while True:
        try:
            value = input(display).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if allow_main and value.lower() == "q":
            return TO_MAIN
        if allow_back and value == "0":
            return BACK
        if value == "":
            print("  输入不能为空，请重新输入")
            continue
        return value


def get_input_allow_empty(prompt, allow_back=True, allow_main=True):
    """获取用户输入，允许空输入。

    Returns:
        用户输入字符串（可能为空）/ BACK / TO_MAIN
    """
    hints = []
    if allow_back:
        hints.append("[0]返回")
    if allow_main:
        hints.append("[q]主菜单")
    hint_str = " ".join(hints)
    display = f"{prompt} ({hint_str}): " if hints else f"{prompt}: "

    while True:
        try:
            value = input(display).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if allow_main and value.lower() == "q":
            return TO_MAIN
        if allow_back and value == "0":
            return BACK
        return value


def print_header(title, width=50):
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def print_step(step):
    print(f"\n  >> {step}")


def select_from_list(options, prompt="请选择", allow_back=True, allow_main=True):
    """展示编号列表让用户选择。

    Returns:
        选中项的索引(0-based) / BACK / TO_MAIN
    """
    for idx, opt in enumerate(options, start=1):
        print(f"  [{idx}] {opt}")
    if allow_back:
        print("  [0] 返回上级")
    if allow_main:
        print("  [q] 返回主菜单")

    while True:
        raw = input(f"\n{prompt} (输入编号): ").strip()
        if raw.lower() == "q" and allow_main:
            return TO_MAIN
        if raw == "0" and allow_back:
            return BACK
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("  请输入有效编号")
