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
from typing import Dict, List, Callable, Union, IO
from utils import Colors


# ---------------- 算法表 ----------------
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

# ---------------- 流式核心 ----------------
BUF = 1 << 20


def multi_hash_stream(
    stream: Union[bytes, IO[bytes]], algos: List[str], buf_size: int = BUF
) -> Dict[str, str]:
    """一次读取，返回 algo->hex 的映射"""
    hashers = {a: ALGO_MAP[a]() for a in algos}
    if isinstance(stream, bytes):  # 小文本
        for h in hashers.values():
            h.update(stream)
        return {a: h.hexdigest() for a, h in hashers.items()}
    # 文件 / stdin
    while chunk := stream.read(buf_size):
        for h in hashers.values():
            h.update(chunk)
    return {a: h.hexdigest() for a, h in hashers.items()}


# ---------------- 输入解析 ----------------
def parse_input(args) -> Union[bytes, IO[bytes]]:
    if args.target == "-":
        print(f"{Colors.OK}从标准输入读取数据{Colors.END}")
        return sys.stdin.buffer
    if args.text:
        print(f"{Colors.OK}按文本内容计算{Colors.END}")
        return args.target.encode("utf-8")
    if os.path.isfile(args.target):
        print(f"{Colors.OK}读取文件: {args.target}{Colors.END}")
        return open(args.target, "rb")
    print(f"{Colors.OK}按文本内容计算{Colors.END}")
    return args.target.encode("utf-8")


# ---------------- 主入口 ----------------
def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(description="计算文件或文本的哈希值")
    parser.add_argument("target", nargs="?", help="文件路径、文本或 '-'")
    parser.add_argument("-a", "--algo", choices=list(ALGO_MAP), help="仅输出指定算法")
    parser.add_argument(
        "-t", "--text", action="store_true", help="强制将 TARGET 视为文本"
    )
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
        parser.error("缺少参数 TARGET（或改用 -l 查看算法列表）")

    try:
        stream = parse_input(args)
    except OSError as e:
        print(f"{Colors.ERR}打开失败: {e}{Colors.END}", file=sys.stderr)
        sys.exit(2)

    # 要算哪些算法
    to_calc = [args.algo] if args.algo else sorted(ALGO_MAP)

    # 统一走 multi_hash_stream
    if hasattr(stream, "seek"):
        stream.seek(0)
    results = multi_hash_stream(stream, to_calc)

    # 输出
    if args.algo:  # 单算法
        print(f"{Colors.BOLD}{args.algo.upper()}{Colors.END}: " f"{results[args.algo]}")
    else:  # 多算法
        print(f"{Colors.BOLD}哈希值:{Colors.END}")
        for k in sorted(ALGO_MAP):
            print(f"  {k.upper()}: {results[k]}")

    if hasattr(stream, "close"):
        stream.close()


if __name__ == "__main__":
    main()
