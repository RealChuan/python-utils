# -*- coding: utf-8 -*-
"""
cli_logger.py
~~~~~~~~~~~~~~~~
一个开箱即用的 loguru 日志配置示例，支持：

1. 彩色控制台输出（自动适配 Windows）。
2. 自动按天分割、保留 7 天、zip 压缩的日志文件。
3. 命令行参数控制日志级别，便于调试。

用法:
    # 查看帮助
    python cli_logger.py -h

    # 默认 INFO 级别
    python cli_logger.py

    # 调试级别
    python cli_logger.py -l DEBUG
"""
from __future__ import annotations

import sys
from pathlib import Path

import loguru
from loguru import logger

# 如果 loguru 版本太旧，建议 pip install -U loguru
assert hasattr(logger, "add"), "请升级 loguru: pip install -U loguru"


def log_init(
    *,
    console_level: str = "INFO",
    log_dir: str = "logs",
    file_level: str = "DEBUG",
) -> None:
    """
    初始化 loguru 日志配置。

    参数:
        console_level: 控制台日志级别，默认 INFO
        log_dir:       日志文件存放目录，默认当前目录下的 logs/
        file_level:    日志文件写入级别，默认 DEBUG（最详细）
    """
    # 1. 移除 loguru 默认的 stderr 处理器，避免重复
    logger.remove()

    # 2. 控制台：带颜色，人类友好
    console_fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        level=console_level,
        format=console_fmt,
        colorize=True,
        backtrace=False,
        diagnose=False,  # 生产环境可设为 False，避免泄露敏感信息
    )

    # 3. 日志文件：按天分割、保留 7 天、zip 压缩、多进程安全
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    file_fmt = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    )
    logger.add(
        log_path / "app_{time:YYYYMMDD}.log",
        level=file_level,
        format=file_fmt,
        rotation="00:00",  # 每天零点新建文件
        retention="7 days",  # 清理旧日志
        compression="zip",  # 压缩历史日志
        enqueue=True,  # 多进程/线程安全
        backtrace=True,  # 记录完整堆栈
        diagnose=True,  # 记录变量值，方便定位
    )

    logger.info(
        "日志初始化完成 | 控制台级别={} | 文件级别={}", console_level, file_level
    )


def log_test() -> None:
    """打印各等级日志，用于快速验证配置是否生效。"""
    text = "hello world"
    logger.debug("debug: {}", text)
    logger.info("info: {}", text)
    logger.success("success: {}", text)
    logger.warning("warning: {}", text)
    logger.error("error: {}", text)
    logger.critical("critical: {}", text)


def build_cli() -> argparse.Namespace:
    """构造简易命令行参数解析器。"""
    import argparse

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
    """CLI 入口函数。"""
    args = build_cli()
    log_init(console_level=args.level)
    log_test()


if __name__ == "__main__":
    main()
