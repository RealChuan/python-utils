# -*- coding: utf-8 -*-
"""
tree.py
递归或非递归打印目录结构，效果类似 Linux 的 tree 命令。

用法:
    python tree.py /path/to/dir          # 仅列一层
    python tree.py /path/to/dir -r       # 递归子目录
    python tree.py -h
"""

import sys
import argparse
from pathlib import Path
from typing import List
from utils import Colors

PREFIX_MIDDLE = "├── "
PREFIX_LAST = "└── "
PREFIX_CONT = "│   "
PREFIX_EMPTY = "    "


def tree(dir_path: Path, prefix: str = "", recursive: bool = False) -> None:
    """打印目录树，recursive 控制是否进入子目录"""
    entries: List[Path] = sorted(
        dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
    )
    for idx, path in enumerate(entries):
        is_last = idx == len(entries) - 1
        connector = PREFIX_LAST if is_last else PREFIX_MIDDLE
        if path.is_dir():
            print(f"{prefix}{connector}{Colors.BOLD}{path.name}{Colors.END}")
            if recursive:  # 仅递归时继续深入
                extension = PREFIX_EMPTY if is_last else PREFIX_CONT
                tree(path, prefix + extension, recursive=True)
        else:
            print(f"{prefix}{connector}{path.name}")


def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(description="打印目录结构")
    parser.add_argument("directory", help="要列出的目录路径")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="递归子目录（默认不递归）"
    )
    args = parser.parse_args(argv)

    root = Path(args.directory).expanduser().resolve()
    if not root.is_dir():
        print(f"{Colors.ERR}错误: {root} 不是有效目录{Colors.END}", file=sys.stderr)
        sys.exit(2)

    print(f"{Colors.OK}{root}{Colors.END}")
    try:
        tree(root, recursive=args.recursive)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.ERR}遍历失败: {e}{Colors.END}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
