# -*- coding: utf-8 -*-
"""
colors.py
跨平台终端颜色工具
"""
import sys


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
