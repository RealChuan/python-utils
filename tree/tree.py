# -*- coding: utf-8 -*-
"""
tree.py —— 递归或非递归打印目录树，效果类似 Linux tree 命令。

用法:
    python tree.py /path/to/dir              # 仅列目录（默认）
    python tree.py /path/to/dir -f           # 目录 + 文件
    python tree.py /path/to/dir -r -f        # 递归且显示文件
    python tree.py /path/to/dir -r -e "*.pyc|__pycache__" -f
    python tree.py /path/to/dir -r --exclude-file excl.txt -f
    python tree.py -h
"""

import sys
import argparse
import fnmatch
from pathlib import Path
from typing import List
from utils import Colors

PREFIX_MIDDLE = "├── "
PREFIX_LAST = "└── "
PREFIX_CONT = "│   "
PREFIX_EMPTY = "    "


def tree(
    dir_path: Path,
    prefix: str = "",
    recursive: bool = False,
    exclude: List[str] = None,
    show_files: bool = False,
) -> None:
    """打印目录树"""
    exclude = exclude or []

    def _is_excluded(p: Path) -> bool:
        abs_path = str(p.absolute())
        for pat in exclude:
            if pat in abs_path or fnmatch.fnmatch(abs_path, pat):
                return True
        return False

    entries: List[Path] = sorted(
        dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
    )
    for idx, path in enumerate(entries):
        if _is_excluded(path):
            continue
        # 新增：默认不显示文件
        if path.is_file() and not show_files:
            continue

        is_last = idx == len(entries) - 1
        connector = PREFIX_LAST if is_last else PREFIX_MIDDLE
        if path.is_dir():
            print(f"{prefix}{connector}{Colors.BOLD}{path.name}{Colors.END}")
            if recursive:
                extension = PREFIX_EMPTY if is_last else PREFIX_CONT
                tree(
                    path,
                    prefix + extension,
                    recursive=True,
                    exclude=exclude,
                    show_files=show_files,
                )
        else:
            print(f"{prefix}{connector}{path.name}")


def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(description="打印目录结构")
    parser.add_argument("directory", help="要列出的目录路径")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="递归子目录（默认不递归）"
    )
    parser.add_argument(
        "-f", "--show-files", action="store_true", help="同时显示文件（默认仅目录）"
    )
    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        action="append",
        default=[],
        help='排除模式，可重复，竖线分隔，例：-e "*.pyc|__pycache__"',
    )
    parser.add_argument(
        "-E",
        "--exclude-file",
        type=Path,
        help="从文本文件读取排除模式，一行一个，# 开头或空行忽略",
    )
    args = parser.parse_args(argv)

    # 收集排除模式
    cmd_patterns = [
        pat.strip()
        for group in args.exclude
        for item in group
        for pat in item.split("|")
        if pat.strip()
    ]
    file_patterns = []
    if args.exclude_file:
        if not args.exclude_file.is_file():
            print(
                f"{Colors.ERR}排除文件不存在: {args.exclude_file}{Colors.END}",
                file=sys.stderr,
            )
            sys.exit(2)
        file_patterns = [
            line.strip()
            for line in args.exclude_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    exclude_patterns = cmd_patterns + file_patterns

    root = Path(args.directory).expanduser().resolve()
    if not root.is_dir():
        print(f"{Colors.ERR}错误: {root} 不是有效目录{Colors.END}", file=sys.stderr)
        sys.exit(2)

    print(f"{Colors.OK}{root}{Colors.END}")
    try:
        tree(
            root,
            recursive=args.recursive,
            exclude=exclude_patterns,
            show_files=args.show_files,
        )
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.ERR}遍历失败: {e}{Colors.END}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
