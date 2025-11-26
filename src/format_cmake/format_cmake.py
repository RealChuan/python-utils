# -*- coding: utf-8 -*-
"""
format_cmake.py —— 立即格式化单个 .cmake 文件，或递归格式化目录下所有 .cmake 文件。

用法:
    python format_cmake.py file.cmake              # 格式化单个文件
    python format_cmake.py dir                     # 递归格式化目录下所有 *.cmake
    python format_cmake.py dir -j 8                # 指定 8 线程并行
    python format_cmake.py -h
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List
from utils import Colors


def _all_site_script_dirs() -> List[Path]:
    dirs: List[Path] = []
    exe_name = "cmake-format.exe" if sys.platform == "win32" else "cmake-format"

    # 1. 当前虚拟环境（最优先）
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        venv_scripts = Path(sys.prefix) / (
            "Scripts" if sys.platform == "win32" else "bin"
        )
        dirs.append(venv_scripts)

    # 2. Windows 用户目录下的 PythonXX\Scripts
    if sys.platform == "win32":
        roaming = Path.home() / "AppData" / "Roaming" / "Python"
        for ver_dir in roaming.glob("Python*"):
            dirs.append(ver_dir / "Scripts")

    # 3. 当前 Python 环境的 Scripts/bin
    dirs.append(Path(sys.prefix) / ("Scripts" if sys.platform == "win32" else "bin"))

    # 4. pip show 给出的 location（cmake-format 官方 wheel 会放 data/）
    try:
        loc = subprocess.check_output(
            [sys.executable, "-m", "pip", "show", "cmake-format"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).splitlines()
        for line in loc:
            if line.startswith("Location:"):
                data_dir = Path(line.split(":", 1)[1].strip()) / "cmake_format" / "data"
                dirs.append(data_dir)
                break
    except Exception:
        pass

    # 5. PATH 里剩下的目录
    for p in os.environ["PATH"].split(os.pathsep):
        dirs.append(Path(p))

    # 6. macOS Homebrew
    if sys.platform == "darwin":
        dirs.append(Path("/usr/local/bin"))
        dirs.append(Path("/opt/homebrew/bin"))

    # 去重并保持顺序
    seen = set()
    return [d for d in dirs if not (d in seen or seen.add(d))]


def locate_cmake_format() -> Path:
    """
    返回 cmake-format 的绝对路径（pathlib.Path）。
    找不到抛 FileNotFoundError。
    """
    exe_name = "cmake-format.exe" if sys.platform == "win32" else "cmake-format"

    # 1. 快速通道
    if (hit := shutil.which(exe_name)) is not None:
        return Path(hit).resolve()

    # 2. 兜底扫描
    for folder in _all_site_script_dirs():
        if not folder.is_dir():
            continue
        candidate = folder / exe_name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            print(f"{Colors.BOLD}cmake-format{Colors.END}：{candidate}")
            return candidate.resolve()

    # 3. 真的找不到
    raise FileNotFoundError(
        "cmake-format 未找到。\n"
        "请先安装：\n"
        "  python -m pip install -U cmake-format\n"
        "并确保所在目录在 PATH 中，或位于当前虚拟环境/用户脚本目录。"
    )


def format_one(exe: Path, path: Path) -> None:
    try:
        subprocess.run([str(exe), "-i", str(path)], check=True)
        print(f"{Colors.OK}formatted  {path}{Colors.END}")
    except subprocess.CalledProcessError as e:
        print(
            f"{Colors.ERR}ERROR      {path}  (return code {e.returncode}){Colors.END}",
            file=sys.stderr,
        )


def find_and_format(exe: Path, root: Path, jobs: int) -> None:
    counter = 0

    def _walk() -> Iterable[Path]:
        nonlocal counter
        for p in root.rglob("*.cmake"):
            if p.is_file():
                counter += 1
                yield p

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        # 把生成器直接扔给 executor.map，它内部会按需 next()
        pool.map(lambda f: format_one(exe, f), _walk())

    if counter == 0:
        print(f"{Colors.WARN}未找到任何 .cmake 文件{Colors.END}")
    else:
        print(f"{Colors.BOLD}All done.{Colors.END}")


def main() -> None:
    parser = argparse.ArgumentParser(description="批量格式化 .cmake 文件")
    parser.add_argument("target", help="单个 .cmake 文件或包含 .cmake 的目录")
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=os.cpu_count(),
        help="并行线程数（默认：CPU 核心数）",
    )
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        print(f"{Colors.ERR}路径不存在: {target}{Colors.END}", file=sys.stderr)
        sys.exit(2)

    exe = locate_cmake_format()

    # 单文件模式
    if target.is_file():
        format_one(exe, target)
        return

    # 目录模式
    find_and_format(exe, target, args.jobs)


if __name__ == "__main__":
    main()
