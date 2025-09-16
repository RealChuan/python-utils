#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
syncthing_monitor.py
~~~~~~~~~~~~~~~~~~~~
轻量级 Syncthing 文件夹实时监控工具

用法:
    # 查看帮助
    python syncthing_monitor.py -h

    # 最小启动（默认读取本机默认配置）
    python syncthing_monitor.py

    # 指定 Syncthing 地址、API-Key、文件夹、轮询间隔
    python syncthing_monitor.py -u http://localhost:8384 \
                                -k QfwYDE2yXj9ysgXWgNNUN6QYkJ95gLoQ \
                                -f default \
                                -i 5
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Dict, Optional

import requests


# ---------- 工具 ----------
def fmt_bytes(num: int) -> str:
    """人性化显示字节"""
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if num < 1024.0:
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PB"


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# ---------- 核心监控 ----------
class SyncthingMonitor:
    def __init__(
        self,
        url: str,
        api_key: str,
        folder: str,
        interval: int = 5,
    ) -> None:
        self.url = url.rstrip("/")
        self.key = api_key
        self.folder = folder
        self.interval = interval
        self.headers = {"X-API-Key": api_key}

        # 上一次采样值，用于计算瞬时速度
        self._last_bytes: Dict[str, int] = {}
        self._last_time = 0.0

    # --- 内部请求 ---
    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        try:
            r = requests.get(
                f"{self.url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            log(f"请求失败 {endpoint}: {e}")
            return None

    # --- 业务接口 ---
    def folder_status(self) -> None:
        """打印文件夹当前状态（idle / syncing / error 等）"""
        data = self._get("/rest/db/status", {"folder": self.folder})
        if not data:
            return
        log(
            f"文件夹状态: {data['state']}  (上次变更: {data.get('stateChanged', 'N/A')})"
        )

    def folder_size(self) -> None:
        """打印总大小与已完成同步大小"""
        data = self._get("/rest/db/status", {"folder": self.folder})
        if not data:
            return
        total = data.get("globalBytes", 0)
        synced = data.get("inSyncBytes", 0)
        log(f"总大小: {fmt_bytes(total)}  |  已同步: {fmt_bytes(synced)}")

    def need_file_count(self) -> None:
        """打印待同步文件数"""
        data = self._get("/rest/db/need", {"folder": self.folder})
        if not data:
            return
        need = (
            len(data.get("progress", []))
            + len(data.get("queued", []))
            + len(data.get("rest", []))
        )
        log(f"待同步文件数: {need}")

    def sync_speed(self) -> None:
        """计算并打印瞬时同步速度（本地 vs 全局）"""
        status = self._get("/rest/db/status", {"folder": self.folder})
        comp = self._get(
            "/rest/db/completion", {"folder": self.folder, "device": "local"}
        )
        if not (status and comp):
            return

        local_bytes = status.get("localBytes", 0)
        global_bytes = comp.get("globalBytes", 0)
        now = time.time()

        if self._last_time:
            dt = now - self._last_time
            if dt > 0:
                speed_local = abs(local_bytes - self._last_bytes.get("local", 0)) / dt
                speed_global = (
                    abs(global_bytes - self._last_bytes.get("global_", 0)) / dt
                )
                log(f"同步速度(本地) : {fmt_bytes(int(speed_local))}/s")
                log(f"同步速度(全局) : {fmt_bytes(int(speed_global))}/s")

        self._last_bytes.update(local=local_bytes, global_=global_bytes)
        self._last_time = now

    # --- 轮询入口 ---
    def run(self) -> None:
        log("开始监控...")
        while True:
            try:
                self.folder_status()
                self.folder_size()
                self.need_file_count()
                self.sync_speed()
                log("-" * 50)
                time.sleep(self.interval)
            except KeyboardInterrupt:
                log("用户中断，退出")
                break


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Syncthing 文件夹实时监控")
    p.add_argument(
        "-u",
        "--url",
        default="http://localhost:8384",
        help="Syncthing 地址，默认 http://localhost:8384",
    )
    p.add_argument(
        "-k", "--api-key", required=True, help="API 密钥（在 Web UI 设置中查看）"
    )
    p.add_argument("-f", "--folder", default="default", help="文件夹 ID，默认 default")
    p.add_argument("-i", "--interval", type=int, default=5, help="轮询间隔(秒)，默认 5")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    monitor = SyncthingMonitor(args.url, args.api_key, args.folder, args.interval)
    monitor.run()


if __name__ == "__main__":
    main()
