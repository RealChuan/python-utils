# -*- coding: utf-8 -*-
"""
m3u8_dl.py
~~~~~~~~~~
通用 M3U8 下载/解密/合并工具（AES-128/CBC）。

用法:
    python m3u8_dl.py -u <m3u8_url> -o <输出.mp4> [-k <key_hex_or_url>] [-t 超时秒数]

示例:
    # 无加密
    python m3u8_dl.py -u https://example.com/index.m3u8 -o movie.mp4

    # 已知 key
    python m3u8_dl.py -u https://example.com/index.m3u8 -o movie.mp4 -k 0123456789abcdef0123456789abcdef

    # key 由服务器下发
    python m3u8_dl.py -u https://example.com/index.m3u8 -o movie.mp4 -k https://example.com/key.bin
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# ------------------ 日志 ------------------
class ColoredLog:
    """极简彩色日志，无额外依赖"""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    @staticmethod
    def info(msg: str) -> None:
        print(f"{ColoredLog.BLUE}[INFO ]{ColoredLog.RESET} {msg}")

    @staticmethod
    def succ(msg: str) -> None:
        print(f"{ColoredLog.GREEN}[SUCC ]{ColoredLog.RESET} {msg}")

    @staticmethod
    def warn(msg: str) -> None:
        print(f"{ColoredLog.YELLOW}[WARN ]{ColoredLog.RESET} {msg}", file=sys.stderr)

    @staticmethod
    def error(msg: str) -> None:
        print(f"{ColoredLog.RED}[ERROR]{ColoredLog.RESET} {msg}", file=sys.stderr)


# ------------------ 核心下载器 ------------------
class M3U8Downloader:
    def __init__(
        self,
        m3u8_url: str,
        output: str,
        key: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.m3u8_url = m3u8_url
        self.output = Path(output)
        self.key: Optional[bytes] = None
        self.iv: Optional[bytes] = None
        self.timeout = timeout
        self.ts_urls: List[str] = []

        # 自动创建输出目录
        self.output.parent.mkdir(parents=True, exist_ok=True)

    # ---------- 1. 解析 ----------
    def parse(self) -> None:
        ColoredLog.info("正在下载与解析 m3u8...")
        try:
            resp = requests.get(self.m3u8_url, timeout=self.timeout)
            resp.raise_for_status()
        except Exception as e:
            ColoredLog.error(f"m3u8 下载失败: {e}")
            sys.exit(1)

        lines = resp.text.splitlines()
        base_url = self.m3u8_url.rsplit("/", 1)[0] + "/"

        for line in lines:
            line = line.strip()
            if line.startswith("#EXT-X-KEY"):
                self._parse_key(line)
            elif line and not line.startswith("#"):
                # 处理相对路径
                self.ts_urls.append(
                    line if line.startswith("http") else base_url + line
                )

        ColoredLog.info(f"共解析到 {len(self.ts_urls)} 个分片")

    def _parse_key(self, line: str) -> None:
        """
        解析 #EXT-X-KEY:METHOD=AES-128,URI="xxx",IV=0x...
        支持十六进制或远程 key 文件
        """
        uri_part = iv_part = ""
        for seg in line.split(","):
            seg = seg.strip()
            if seg.startswith("URI="):
                uri_part = seg[4:].strip('"')
            elif seg.startswith("IV="):
                iv_part = seg[3:].strip('"')

        # 下载 key
        if uri_part.startswith("http"):
            try:
                key_bytes = requests.get(uri_part, timeout=self.timeout).content
            except Exception as e:
                ColoredLog.error(f"key 下载失败: {e}")
                sys.exit(1)
        else:
            # 直接当成 hex
            try:
                key_bytes = bytes.fromhex(uri_part)
            except ValueError:
                ColoredLog.error("key 格式错误，应为 hex 或 http(s) 链接")
                sys.exit(1)

        self.key = key_bytes
        self.iv = bytes.fromhex(iv_part[2:]) if iv_part.startswith("0x") else key_bytes
        ColoredLog.info(f"获取加密 key={self.key.hex()} iv={self.iv.hex()}")

    # ---------- 2. 下载 ----------
    def download(self) -> None:
        ColoredLog.info("开始下载分片...")
        temp_dir = self.output.with_suffix(".parts")
        temp_dir.mkdir(exist_ok=True)

        for idx, ts_url in enumerate(self.ts_urls, 1):
            retry = 3
            while retry:
                try:
                    resp = requests.get(ts_url, timeout=self.timeout)
                    resp.raise_for_status()
                    break
                except Exception as e:
                    retry -= 1
                    ColoredLog.warn(
                        f"[{idx}/{len(self.ts_urls)}] 下载失败: {e}，剩余重试 {retry}"
                    )
                    time.sleep(1)
            else:
                ColoredLog.error("多次重试仍失败，程序终止")
                sys.exit(1)

            data = resp.content
            if self.key:
                data = self._decrypt(data)

            temp_file = temp_dir / f"{idx:06}.ts"
            temp_file.write_bytes(data)
            ColoredLog.succ(f"[{idx}/{len(self.ts_urls)}] 完成")

    def _decrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        return unpad(cipher.decrypt(data), AES.block_size)

    # ---------- 3. 合并 ----------
    def merge(self) -> None:
        ColoredLog.info("正在合并分片...")
        temp_dir = self.output.with_suffix(".parts")
        with open(self.output, "wb") as fout:
            for ts_file in sorted(temp_dir.glob("*.ts")):
                fout.write(ts_file.read_bytes())
        ColoredLog.succ(f"合并完成 -> {self.output.absolute()}")

    # ---------- 4. 清理 ----------
    def clean(self) -> None:
        temp_dir = self.output.with_suffix(".parts")
        for f in temp_dir.glob("*.ts"):
            f.unlink()
        temp_dir.rmdir()

    # ---------- 5. 一键执行 ----------
    def run(self) -> None:
        self.parse()
        self.download()
        self.merge()
        self.clean()
        ColoredLog.succ("全部任务完成！")


# ------------------ CLI ------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="M3U8 下载/解密/合并工具")
    parser.add_argument("-u", "--url", required=True, help="m3u8 地址")
    parser.add_argument("-o", "--output", required=True, help="输出文件（mp4/ts 均可）")
    parser.add_argument(
        "-k", "--key", help="16 字节 hex 或 key 文件 url（留空自动读取 m3u8）"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="超时秒数，默认 30"
    )
    args = parser.parse_args()

    dl = M3U8Downloader(args.url, args.output, args.key, args.timeout)
    dl.run()


if __name__ == "__main__":
    main()
