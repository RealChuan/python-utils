# -*- coding: utf-8 -*-
"""
webdav.py
~~~~~~~~~
轻量级 WebDAV 客户端封装（支持常用方法 + 下载/上传/删除/移动等）

用法:
    # 1. 查看帮助
    python webdav.py -h

    # 2. 上传本地文件
    python webdav.py -u https://example.com/dav/ -U user -P pass put local.txt /remote.txt

    # 3. 下载文件
    python webdav.py -u https://example.com/dav/ -U user -P pass get /remote.txt local.txt

    # 4. 删除文件
    python webdav.py -u https://example.com/dav/ -U user -P pass delete /remote.txt

    # 5. 移动文件
    python webdav.py -u https://example.com/dav/ -U user -P pass move /old.txt /new.txt
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import requests
import urllib3

# 关闭 SSL 警告（默认禁用，可通过 --verify 打开）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- 日志 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("webdav")


# ---------- 核心客户端 ----------
class WebDAV:
    """轻量级 WebDAV 客户端"""

    def __init__(
        self, base_url: str, username: str, password: str, verify_ssl: bool = False
    ) -> None:
        self.base = base_url.rstrip("/")
        self.sess = requests.Session()
        self.sess.auth = (username, password)
        self.sess.verify = verify_ssl
        # 部分服务器需要 XML 头，这里先留空，按需添加
        self.sess.headers.update({"User-Agent": "python-webdav/1.0"})

    # --- 内部请求 ---
    def _req(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base}{path}"
        logger.debug(f"{method} {url}")
        try:
            resp = self.sess.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            logger.error(f"HTTPError {e.response.status_code}: {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"RequestException: {e}")
            raise

    # --- 公开 API ---
    def get(self, remote: str, local: str) -> None:
        """下载文件"""
        with self._req("GET", remote, stream=True) as r:
            Path(local).write_bytes(r.content)
        logger.info(f"downloaded  {remote} -> {local}")

    def put(self, local: str, remote: str) -> None:
        """上传文件"""
        data = Path(local).read_bytes()
        self._req("PUT", remote, data=data)
        logger.info(f"uploaded    {local} -> {remote}")

    def delete(self, remote: str) -> None:
        """删除文件/空目录"""
        self._req("DELETE", remote)
        logger.info(f"deleted     {remote}")

    def move(self, remote_src: str, remote_dst: str) -> None:
        """移动/重命名"""
        self._req(
            "MOVE", remote_src, headers={"Destination": f"{self.base}{remote_dst}"}
        )
        logger.info(f"moved       {remote_src} -> {remote_dst}")

    def propfind(self, remote: str = "/") -> int:
        """返回目录项数量（简单统计）"""
        xml = """<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
  <d:prop><d:displayname/></d:prop>
</d:propfind>"""
        r = self._req(
            "PROPFIND",
            remote,
            data=xml,
            headers={"Depth": "1", "Content-Type": "application/xml"},
        )
        # 粗略统计 <response> 节点数
        count = r.text.count("<d:response>") or r.text.count("<response>")
        logger.info(f"propfind    {remote} -> {count} entries")
        return count


# ---------- CLI ----------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="轻量级 WebDAV 客户端")
    p.add_argument(
        "-u",
        "--url",
        required=True,
        help="WebDAV 基础地址，如 https://example.com/dav/",
    )
    p.add_argument("-U", "--username", required=True, help="用户名")
    p.add_argument("-P", "--password", required=True, help="密码")
    p.add_argument("--verify", action="store_true", help="验证 SSL 证书（默认忽略）")
    sub = p.add_subparsers(dest="cmd", required=True, help="子命令")

    # get
    get_p = sub.add_parser("get", help="下载文件")
    get_p.add_argument("remote", help="远程路径（含文件名）")
    get_p.add_argument("local", help="本地保存路径")
    # put
    put_p = sub.add_parser("put", help="上传文件")
    put_p.add_argument("local", help="本地文件路径")
    put_p.add_argument("remote", help="远程路径（含文件名）")
    # delete
    del_p = sub.add_parser("delete", help="删除远程文件")
    del_p.add_argument("remote", help="远程路径")
    # move
    move_p = sub.add_parser("move", help="移动/重命名")
    move_p.add_argument("src", help="源远程路径")
    move_p.add_argument("dst", help="目标远程路径")
    # propfind
    prop_p = sub.add_parser("list", help="列目录（简单统计条目数）")
    prop_p.add_argument("remote", nargs="?", default="/", help="远程目录，默认根目录")

    return p


def main(argv: Optional[list] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    dav = WebDAV(args.url, args.username, args.password, verify_ssl=args.verify)

    try:
        if args.cmd == "get":
            dav.get(args.remote, args.local)
        elif args.cmd == "put":
            dav.put(args.local, args.remote)
        elif args.cmd == "delete":
            dav.delete(args.remote)
        elif args.cmd == "move":
            dav.move(args.src, args.dst)
        elif args.cmd == "list":
            dav.propfind(args.remote)
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
