#!/usr/bin/env python3
"""零依赖启动：自动解压 wheel 包，无需 pip / venv / apt。

首次运行:
    python3 run.py
    → 自动将 wheels/*.whl 解压到 _lib/ → 启动 CLI

之后运行:
    python3 run.py
    → _lib/ 已存在 → 直接启动 CLI

无需 pip、无需 venv、无需 apt-get install、无需联网。
唯一前提: 系统装有 Python 3.6+（标准库自带的 zipfile 即可）。
"""

import os
import shutil
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHEELS_DIR = os.path.join(SCRIPT_DIR, "wheels")
LIB_DIR = os.path.join(SCRIPT_DIR, "_lib")
FLAG_FILE = os.path.join(LIB_DIR, ".installed")


def _extract_wheels():
    """首次运行：解压所有 wheel 文件到 _lib/"""
    if os.path.exists(LIB_DIR):
        shutil.rmtree(LIB_DIR)
    os.makedirs(LIB_DIR)

    for filename in sorted(os.listdir(WHEELS_DIR)):
        if not filename.endswith(".whl"):
            continue
        whl_path = os.path.join(WHEELS_DIR, filename)
        with zipfile.ZipFile(whl_path, "r") as zf:
            zf.extractall(LIB_DIR)

    with open(FLAG_FILE, "w", encoding="utf-8") as f:
        f.write("ok")


def main():
    if not os.path.isfile(FLAG_FILE):
        print("首次运行，正在解压依赖（仅此一次）...")
        _extract_wheels()
        print("完成！\n")

    sys.path.insert(0, LIB_DIR)
    sys.path.insert(0, SCRIPT_DIR)

    from excel_tools.cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
