# -*- coding: utf-8 -*-
"""
resolve.py
获取指定域名的 IPv4/IPv6 地址、主机名、别名等信息。

用法:
    python resolve.py www.baidu.com
    python resolve.py -h
"""
import socket
import sys
import argparse
from typing import List, Tuple


class Colors:
    """跨平台终端颜色"""

    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @staticmethod
    def enable_windows_color() -> None:
        """Windows 10+ 启用 ANSI 转义序列"""
        if sys.platform == "win32":
            import os

            os.system("")


Colors.enable_windows_color()


def get_host_info(domain: str) -> Tuple[List[str], List[str], str, List[str]]:
    """
    解析域名，返回:
        ipv4_list, ipv6_list, hostname, alias_list
    遇到异常直接抛 socket.gaierror
    """
    # family=0 表示获取所有族，socktype=0 表示任意类型
    info = socket.getaddrinfo(domain, None)

    ipv4 = sorted({item[4][0] for item in info if item[0] == socket.AF_INET})
    ipv6 = sorted({item[4][0] for item in info if item[0] == socket.AF_INET6})
    # getaddrinfo 返回的三元组 (hostname, aliaslist, ipaddrlist)
    hostname, aliaslist, _ = socket.gethostbyname_ex(domain)
    return ipv4, ipv6, hostname, sorted(aliaslist)


def print_section(title: str, items: List[str]) -> None:
    """统一输出格式：标题 + 列表，空列表给出提示"""
    print(f"{Colors.BOLD}{title}:{Colors.END}")
    if not items:
        print("  (无)")
    for it in items:
        print(f"  {it}")


def main(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(
        description="获取域名的 IPv4/IPv6、主机名、别名等信息"
    )
    parser.add_argument("domain", help="要查询的域名，例如 www.baidu.com")
    args = parser.parse_args(argv)

    try:
        ipv4, ipv6, hostname, aliases = get_host_info(args.domain)
    except socket.gaierror as e:
        print(f"{Colors.ERR}解析失败: {e}{Colors.END}", file=sys.stderr)
        sys.exit(2)

    print_section("IPv4 地址", ipv4)
    print_section("IPv6 地址", ipv6)
    print_section("主机名", [hostname])
    print_section("别名", aliases)


if __name__ == "__main__":
    main()
