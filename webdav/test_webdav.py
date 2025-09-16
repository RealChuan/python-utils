# -*- coding: utf-8 -*-
"""
test_webdav.py
~~~~~~~~~~~~~~
针对 webdav.py 的单元测试
* 依赖本地 WebDAV 服务：docker run -d -p 8080:80 -v /tmp/dav:/data davserver/davserver
* 若 8080 无法连接，自动跳过在线用例
"""
from __future__ import annotations

import os
import sys
import unittest
import requests
from pathlib import Path

# 把当前目录加入搜索路径，以便 import webdav
sys.path.insert(0, os.path.dirname(__file__))
import webdav  # noqa: E402

# ---------- 配置 ----------
LOCAL_FILE = Path(__file__)  # 用自身文件当测试上传样本
REMOTE_FILE = "/test_webdav.txt"  # 远程路径
BASE_URL = "http://localhost:8080"  # WebDAV 根地址
USER = "user"
PWD = "user"


class WebDAVTest(unittest.TestCase):
    """测试 webdav.WebDAV 类核心方法"""

    @classmethod
    def setUpClass(cls):
        cls.client = webdav.WebDAV(BASE_URL, USER, PWD, verify_ssl=False)
        # 探测服务是否在线
        try:
            cls.client.propfind("/")
            cls.online = True
        except Exception as e:
            cls.online = False
            print(f"[WARN] WebDAV 服务不可用，跳过在线用例：{e}")

    def setUp(self):
        if not self.online:
            self.skipTest("WebDAV 服务未启动")

    # --- 基础 CRUD ---

    def test_put_get_delete(self):
        """上传 -> 下载 -> 删除 闭环"""
        # 上传
        self.client.put(LOCAL_FILE, REMOTE_FILE)
        # 下载
        down_file = LOCAL_FILE.with_suffix(".down")
        self.client.get(REMOTE_FILE, down_file)
        self.assertEqual(LOCAL_FILE.read_bytes(), down_file.read_bytes())
        down_file.unlink()  # 清理
        # 删除
        self.client.delete(REMOTE_FILE)

    def test_move(self):
        """移动/重命名"""
        self.client.put(LOCAL_FILE, REMOTE_FILE)
        new_path = "/moved.txt"
        self.client.move(REMOTE_FILE, new_path)
        # 确认移动成功（下载不抛异常即可）
        self.client.get(new_path, "/tmp/moved.tmp")
        Path("/tmp/moved.tmp").unlink()
        self.client.delete(new_path)

    def test_mkcol_propfind(self):
        """建目录 + 列目录"""
        col = "/testdir"
        self.client.mkcol(col)
        count = self.client.propfind(col)
        self.assertGreaterEqual(count, 1)  # 至少包含自身
        self.client.delete(col)


# ---------- 主入口 ----------
if __name__ == "__main__":
    # 支持命令行参数 -v 查看详细日志
    unittest.main(verbosity=2)
