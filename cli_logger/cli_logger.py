# -*- coding: utf-8 -*-
"""
cli_logger.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
开箱即用的 loguru 日志配置包，支持：

1. 彩色控制台输出（自动适配 Windows）。
2. 按天分割、保留 7 天、zip 压缩、多进程安全。
3. 日志文件名 = 调用脚本名（或自定义前缀）。
4. 通过环境变量 LOG_LEVEL / LOG_FILE_LEVEL 动态调整级别。
5. 既可当脚本直接跑，也可被其它模块 import，零侵入。

用法
----
# 1. 当作包使用（推荐）
from cli_logger import log_init, logger
logger.info("hello world")

# 2. 当作脚本运行
python cli_logger.py -l DEBUG

# 3. 自定义日志文件名前缀
from cli_logger import log_init
log_init(file_prefix="web")
"""
from __future__ import annotations

import argparse
import inspect
import os
import sys
import socket
import pathlib

from loguru import logger


# ---------- 默认路径/级别 ----------
_DEFAULT_LOG_DIR = pathlib.Path(__file__).parent.parent / "logs"
_CONSOLE_LVL = os.getenv("LOG_LEVEL", "INFO").upper()
_FILE_LVL = os.getenv("LOG_FILE_LEVEL", "DEBUG").upper()


def log_init(
    *,
    console_level: str = _CONSOLE_LVL,
    log_dir: str | pathlib.Path = _DEFAULT_LOG_DIR,
    file_level: str = _FILE_LVL,
    file_prefix: str | None = None,
) -> None:
    """
    初始化 loguru 日志配置。

    参数
    ----
    console_level : str
        控制台日志级别，默认读取环境变量 LOG_LEVEL，否则 INFO
    log_dir : str | Path
        日志文件存放目录，默认仓库根目录下的 logs/
    file_level : str
        日志文件写入级别，默认读取环境变量 LOG_FILE_LEVEL，否则 DEBUG
    file_prefix : str | None
        日志文件名前缀，默认取调用脚本名（不含扩展名）
    """
    # 1. 移除默认 handler
    logger.remove()

    # 2. 控制台
    console_fmt = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{thread: >5}</cyan> | "  # <-- 新增
        "<magenta>{name}</magenta>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        level=console_level,
        format=console_fmt,
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    # 3. 日志文件：按天分割、保留 7 天、zip 压缩、多进程安全
    log_path = pathlib.Path(log_dir).expanduser().resolve()
    log_path.mkdir(parents=True, exist_ok=True)

    # 自动获取调用者脚本名
    if file_prefix is None:
        # 0=当前函数，1=显式调用者（业务脚本）
        caller_file = pathlib.Path(inspect.stack()[1].filename)
        file_prefix = caller_file.stem

    prefix = file_prefix
    hostname = socket.gethostname()
    pid = os.getpid()

    file_fmt = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{thread: >5} | "
        "{name}:{function}:{line} - {message}"
    )
    logger.add(
        log_path / f"{prefix}_{hostname}_{pid}_{{time:YYYYMMDD_HHmmss}}.log",
        level=file_level,
        format=file_fmt,
        rotation="00:00",
        retention="7 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info(
        f"日志初始化完成 | 控制台级别={console_level} | "
        f"文件级别={file_level} | 日志目录={log_path} | 前缀={prefix}"
    )


def log_test() -> None:
    """打印各等级日志，用于快速验证配置是否生效。"""
    text = "hello world"
    logger.debug(f"debug: {text}")
    logger.info(f"info: {text}")
    logger.success(f"success: {text}")
    logger.warning(f"warning: {text}")
    logger.error(f"error: {text}")
    logger.critical(f"critical: {text}")


# ---------- 脚本入口 ----------
def _build_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="loguru 日志配置示例，支持控制台与文件双通道输出。"
    )
    parser.add_argument(
        "-l",
        "--level",
        choices=["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="控制台日志级别（默认 INFO）",
    )
    return parser.parse_args()


def main() -> None:
    args = _build_cli()
    log_init(console_level=args.level)
    log_test()


if __name__ == "__main__":
    main()
