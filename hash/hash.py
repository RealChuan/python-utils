# -*- coding: utf-8 -*-
"""
hash.py
计算给定文件或文本的哈希值（MD5/SHA-1/SHA-2/SHA-3/BLAKE2/BLAKE3）。

用法:
    python hash.py FILE_OR_TEXT
    python hash.py -a blake3 FILE
    echo -n "hello" | python hash.py -
    python hash.py -l
    python hash.py -h
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from typing import Dict, List, Callable
from utils import Colors


# ---------- 算法表 ----------
ALGO_MAP: Dict[str, Callable[[], "hashlib._Hash"]] = {}

# 标准库自带
for _name in (
    "md5",
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
):
    ALGO_MAP[_name] = getattr(hashlib, _name)

# BLAKE2b
ALGO_MAP["blake2b"] = hashlib.blake2b

# BLAKE3（可选）
try:
    import blake3

    ALGO_MAP["blake3"] = lambda: blake3.blake3()
except ImportError:
    pass


# ---------- 工具 ----------
def calc_hash(data: bytes, algo: str) -> str:
    """计算指定算法哈希值，返回十六进制字符串"""
    h = ALGO_MAP[algo]()
    h.update(data)
    return h.hexdigest()


def read_target(target: str) -> bytes:
    """从文件、文本或 stdin 读取二进制数据"""
    if target == "-":
        print(f"{Colors.OK}从标准输入读取数据{Colors.END}")
        return sys.stdin.buffer.read()
    if os.path.isfile(target):
        print(f"{Colors.OK}读取文件: {target}{Colors.END}")
        with open(target, "rb") as f:
            return f.read()
    print(f"{Colors.OK}按文本内容计算{Colors.END}")
    return target.encode("utf-8")


# ---------- 主入口 ----------
def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(description="计算文件或文本的哈希值")
    parser.add_argument("target", nargs="?", help="文件路径、文本或 '-' 表示 stdin")
    parser.add_argument("-a", "--algo", choices=list(ALGO_MAP), help="仅输出指定算法")
    parser.add_argument("-l", "--list", action="store_true", help="列出支持的算法")
    args = parser.parse_args(argv)

    if args.list:
        print(f"{Colors.BOLD}本机支持的算法:{Colors.END}")
        for k in sorted(ALGO_MAP):
            print(f"  {k.upper()}")
        if "blake3" not in ALGO_MAP:
            print(f"{Colors.WARN}提示：pip install blake3 可获得更高性能{Colors.END}")
        return

    if args.target is None:
        parser.error("缺少参数 target（或改用 -l 查看算法列表）")

    try:
        data = read_target(args.target)
    except OSError as e:
        print(f"{Colors.ERR}读取失败: {e}{Colors.END}", file=sys.stderr)
        sys.exit(2)

    if args.algo:
        print(
            f"{Colors.BOLD}{args.algo.upper()}{Colors.END}: {calc_hash(data, args.algo)}"
        )
    else:
        print(f"{Colors.BOLD}哈希值:{Colors.END}")
        for k in sorted(ALGO_MAP):
            print(f"  {k.upper()}: {calc_hash(data, k)}")


if __name__ == "__main__":
    main()
