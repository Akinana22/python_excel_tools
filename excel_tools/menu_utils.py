"""通用菜单工具：输入获取、清屏、退出处理"""

import os
import sys

EXIT_KEYWORD = "q"
BACK_KEYWORD = "0"


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_input(prompt, allow_back = True, allow_quit = True):
    """获取用户输入，支持返回上级和退出。

    Returns:
        用户输入的字符串，若返回 None 表示用户选择退出，
        若返回 BACK_KEYWORD 表示用户选择返回上级。
    """
    hints = []
    if allow_back:
        hints.append("[0]返回")
    if allow_quit:
        hints.append("[q]退出")
    hint_str = " ".join(hints)
    display_prompt = f"{prompt} ({hint_str}): "

    while True:
        try:
            value = input(display_prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出程序")
            sys.exit(0)

        if allow_quit and value.lower() == EXIT_KEYWORD:
            print("\n已退出程序")
            sys.exit(0)
        if allow_back and value == BACK_KEYWORD:
            return BACK_KEYWORD
        if value == "":
            print("  输入不能为空，请重新输入")
            continue
        return value


def get_input_or_back(prompt):
    """获取输入，允许返回上级和退出。返回 None 表示用户取消。"""
    result = get_input(prompt, allow_back=True, allow_quit=True)
    if result == BACK_KEYWORD:
        return None
    return result


def print_header(title, width = 50):
    """打印格式化标题。"""
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def print_step(step):
    """打印步骤提示。"""
    print(f"\n  >> {step}")


def select_from_list(options, prompt = "请选择", allow_back = True):
    """展示编号列表让用户选择，返回选中的索引(0-based)，None 表示取消或返回。

    Args:
        options: 选项文本列表
        prompt: 提示语
        allow_back: 是否显示返回选项

    Returns:
        选中的索引，None 表示用户选择返回
    """
    for idx, opt in enumerate(options, start=1):
        print(f"  [{idx}] {opt}")
    if allow_back:
        print(f"  [0] 返回上级")

    while True:
        raw = input(f"\n{prompt} (输入编号, [0]返回, [q]退出): ").strip()
        if raw.lower() == "q":
            print("\n已退出程序")
            sys.exit(0)
        if raw == "0" and allow_back:
            return None
        if not raw.isdigit():
            print("  请输入有效编号")
            continue
        num = int(raw)
        if 1 <= num <= len(options):
            return num - 1
        else:
            print(f"  请输入 1~{len(options)} 之间的编号")
