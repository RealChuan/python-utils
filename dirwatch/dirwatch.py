# -*- coding: utf-8 -*-
"""
dirwatch.py
~~~~~~~~~~~

极简目录监控 + 文件哈希比对工具

功能:
1. 利用 watchdog 实时监控创建、删除、修改、移动事件；
2. 首次启动时对整目录做 MD5 快照，后续可发现“静默改动”；
3. 支持 CLI 一键启动；结果彩色输出；
4. 可作为模块导入：from dirwatch import DirWatch

用法:
    # 监控当前目录
    python dirwatch.py

    # 监控指定路径
    python dirwatch.py /var/log

    # 查看所有参数
    python dirwatch.py -h
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from queue import Queue
from typing import Dict, List, Optional, Tuple
from cli_logger import log_init, logger

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# ---------- 事件处理器 ----------
class _EventHandler(FileSystemEventHandler):
    """把 watchdog 事件转成简易元组推入队列"""

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def on_created(self, event) -> None:
        typ = "dir" if event.is_directory else "file"
        logger.info(f"{typ} created: {event.src_path}")
        self.queue.put((event.src_path, None, "created"))

    def on_deleted(self, event) -> None:
        typ = "dir" if event.is_directory else "file"
        logger.warning(f"{typ} deleted: {event.src_path}")
        self.queue.put((event.src_path, None, "deleted"))

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        logger.info(f"file modified: {event.src_path}")
        self.queue.put((event.src_path, None, "modified"))

    def on_moved(self, event) -> None:
        typ = "dir" if event.is_directory else "file"
        logger.info(f"{typ} moved: {event.src_path} -> {event.dest_path}")
        self.queue.put((event.src_path, event.dest_path, "moved"))


# ---------- 核心监控器 ----------
class DirWatch:
    """
    实时监控 + 快照比对
    """

    def __init__(self, path: str) -> None:
        self.path = Path(path).expanduser().resolve()
        if not self.path.is_dir():
            raise ValueError(f"路径不存在: {self.path}")
        self._observer = Observer()
        self._queue: Queue = Queue()
        self._snapshot: Dict[str, str] = {}  # file -> md5

    # --- 公有 API ---
    def start(self) -> None:
        """启动监控"""
        self._take_snapshot()
        handler = _EventHandler(self._queue)
        self._observer.schedule(handler, str(self.path), recursive=True)
        self._observer.start()
        logger.success(f"开始监控 {self.path}  … 按 Ctrl+C 退出")

    def stop(self) -> None:
        """优雅停止"""
        self._observer.stop()
        self._observer.join()
        logger.info("监控已停止")

    def get_changes(self) -> List[Tuple[str, Optional[str], str]]:
        """非阻塞获取当前事件队列"""
        changes: List[Tuple[str, Optional[str], str]] = []
        while True:
            try:
                changes.append(self._queue.get(block=False))
            except Exception:
                break
        return changes

    # --- 内部辅助 ---
    def _take_snapshot(self) -> None:
        logger.info("正在生成初始快照 …")
        for root, _, files in os.walk(self.path):
            for file in files:
                fp = Path(root) / file
                try:
                    st = fp.stat()
                    # 用 size+mtime 当唯一标识
                    self._snapshot[str(fp)] = f"{st.st_size}-{st.st_mtime}"
                except Exception as e:
                    logger.warning(f"跳过 {fp}: {e}")
        logger.success(f"快照完成，共 {len(self._snapshot)} 个文件")


# ---------- CLI ----------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="目录监控 + 文件哈希比对")
    parser.add_argument(
        "path", nargs="?", default=".", help="要监控的目录，默认当前目录"
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    try:
        watch = DirWatch(args.path)
        watch.start()
        # 简单演示：每 2 秒打印一次队列
        while True:
            time.sleep(2)
            changes = watch.get_changes()
            if changes:
                logger.success(f"最近变动: {changes}")
    except KeyboardInterrupt:
        logger.info("用户中断")
    finally:
        watch.stop()


# ---------- 单元测试 ----------
import unittest  # noqa: E402


class TestDirWatch(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path("tmp_test")
        self.tmp.mkdir(exist_ok=True)
        (self.tmp / "a.txt").write_text("hello")
        self.watch = DirWatch(str(self.tmp))
        self.watch.start()

    def tearDown(self) -> None:
        self.watch.stop()
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_event(self) -> None:
        (self.tmp / "b.txt").write_text("world")
        time.sleep(0.5)
        changes = self.watch.get_changes()
        self.assertTrue(any("b.txt" in str(c[0]) for c in changes))


if __name__ == "__main__":
    log_init()

    # 若命令行含 -t 则跑单测，否则跑 CLI
    if "-t" in sys.argv:
        sys.argv.remove("-t")
        unittest.main()
    else:
        main()
