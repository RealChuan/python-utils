# -*- coding: utf-8 -*-
"""
procmon.py
~~~~~~~~~~
按**进程名**实时监控 CPU、内存、线程数、句柄数（多进程累加）

用法:
    python procmon.py -p chrome      # 监控所有含 chrome 的进程
    python procmon.py -p java -i 1 -d 120 -s java.png
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Tuple
from cli_logger import log_init, logger

import psutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class ProcessMonitor:
    def __init__(
        self,
        process_name: str,
        interval: int = 3,
        duration: int = 60,
        save_path: Optional[str] = None,
    ) -> None:
        self.process_name = process_name.lower()
        self.interval = interval
        self.duration = duration
        self.save_path = save_path

        # 数据队列
        self.time_sec: List[int] = []
        self.cpu: List[float] = []
        self.mem: List[float] = []  # RSS 内存 MB
        self.threads: List[int] = []
        self.handles: List[int] = []

        # 画布
        self.fig, self.axes = plt.subplots(2, 2, figsize=(10, 8))
        self.fig.suptitle(f'Process Monitor: "{self.process_name}"')
        self.ax_cpu, self.ax_mem, self.ax_thd, self.ax_hdl = self.axes.flat
        self._style_axis()

        # 动画
        self.ani = animation.FuncAnimation(
            self.fig,
            self._update,
            interval=self.interval * 1000,
            blit=False,
            cache_frame_data=False,
        )

    # ---------- 样式 ----------
    def _style_axis(self) -> None:
        self.ax_cpu.set_title("CPU %")
        self.ax_cpu.set_ylim(0, 100)
        self.ax_mem.set_title("Memory MB")
        self.ax_thd.set_title("Threads")
        self.ax_hdl.set_title("Handles / FDs")

    # ---------- 采集 ----------
    def _find_pids(self) -> List[psutil.Process]:
        """按名字查找所有匹配进程（不区分大小写）"""
        procs = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                if self.process_name in p.info["name"].lower():  # type: ignore
                    procs.append(psutil.Process(p.info["pid"]))  # type: ignore
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return procs

    def _sample(self) -> Tuple[float, float, int, int]:
        """返回累加值：cpu%, rss(MB), threads, handles"""
        procs = self._find_pids()
        if not procs:
            return 0.0, 0.0, 0, 0

        cpu = rss = threads = handles = 0
        for p in procs:
            try:
                cpu += p.cpu_percent()
                rss += p.memory_info().rss
                threads += p.num_threads()
                handles += len(p.open_files()) + len(p.net_connections())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cpu, rss / 1024 / 1024, threads, handles

    # ---------- 刷新 ----------
    def _update(self, frame: int) -> None:
        t = frame * self.interval
        cpu, mem, thd, hdl = self._sample()

        logger.info(
            f"时间={t}s  CPU={cpu:.2f}%  内存={mem:.2f}MB  线程={thd}  句柄={hdl}"
        )

        self.time_sec.append(t)
        self.cpu.append(cpu)
        self.mem.append(mem)
        self.threads.append(thd)
        self.handles.append(hdl)

        self._draw_plots()

        if t >= self.duration:
            if self.save_path:
                self.fig.savefig(self.save_path)
                logger.success(f"图表已保存 → {self.save_path}")
            plt.close(self.fig)

    def _draw_plots(self) -> None:
        for ax in self.axes.flat:
            ax.clear()
            ax.set_xlabel("Time (s)")

        self.ax_cpu.plot(self.time_sec, self.cpu, color="red", label="CPU %")
        self.ax_mem.plot(self.time_sec, self.mem, color="green", label="RSS MB")
        self.ax_thd.plot(self.time_sec, self.threads, color="blue", label="Threads")
        self.ax_hdl.plot(self.time_sec, self.handles, color="orange", label="Handles")

        for ax in self.axes.flat:
            ax.legend(loc="upper left")

    # ---------- 启动 ----------
    def run(self) -> None:
        if not self._find_pids():
            logger.error(f'未找到含 "{self.process_name}" 的进程，程序退出')
            sys.exit(1)
        logger.info(
            f"开始监控 → 间隔={self.interval}s  时长={self.duration}s  保存={self.save_path}"
        )
        plt.show()


# ---------- CLI ----------
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按进程名实时监控资源曲线")
    parser.add_argument("-p", "--process", required=True, help="进程名称（片段即可）")
    parser.add_argument(
        "-i", "--interval", type=int, default=3, help="采样间隔(秒)，默认 3"
    )
    parser.add_argument(
        "-d", "--duration", type=int, default=60, help="总时长(秒)，默认 60"
    )
    parser.add_argument("-s", "--save", help="结束后折线图保存路径，默认不保存")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        ProcessMonitor(args.process, args.interval, args.duration, args.save).run()
    except KeyboardInterrupt:
        logger.info("用户中断，已退出")


if __name__ == "__main__":
    log_init()
    main()
