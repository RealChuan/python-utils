# Python Utils

- [简体中文](README.md)
- [English](README.en.md)

让开发和生活都更快乐的小工具集合 🧰

## 📦 工具列表

| 模块 | 描述 | 主要文件 |
|---|---|---|
| **cli_logger** | loguru 日志配置示例，控制台 + 文件双通道输出 | [`cli_logger.py`](cli_logger/cli_logger.py) |
| **dirwatch** | 实时监控文件夹变化（增/删/改/重命名） | [`dirwatch.py`](dirwatch/dirwatch.py) |
| **format_cmake** | 格式化 CMake 文件（单个或递归目录） | [`format_cmake.py`](format_cmake/format_cmake.py) |
| **hash** | 计算文件或文本的哈希值（MD5/SHA-1/SHA-2/SHA-3/BLAKE2/BLAKE3） | [`hash.py`](hash/hash.py) |
| **image-toolkit** | 图片格式转换工具 + 一键生成/解析`.icns` / `.ico` | [`convert_img.py`](image-toolkit/convert_img.py) / [`dump_icns.py`](image-toolkit/dump_icns.py) / [`dump_ico.py`](image-toolkit/dump_ico.py) / [`make_icns.py`](image-toolkit/make_icns.py) / [`make_ico.py`](image-toolkit/make_ico.py) |
| **m3u8_download** | m3u8 下载器，自动合并 ts 为单个视频 | [`m3u8_dl.py`](m3u8_download/m3u8_dl.py) |
| **procmon** | 按进程名实时监控 CPU/内存/线程/句柄 | [`procmon.py`](procmon/procmon.py) |
| **resolve** | 域名解析工具，快速获取 IP、端口、协议信息 | [`resolve.py`](resolve/resolve.py) |
| **tree** | 可视化目录树生成工具 | [`tree.py`](tree/tree.py) |
| **utils** | 通用工具库（颜色输出等） | [`colors.py`](utils/colors.py) |
| **sync_req** | 依赖同步工具，从 pyproject.toml 生成 requirements.txt | [`sync_req.py`](sync_req.py) |

## 🚀 快速开始

### 安装依赖

推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate

# 或使用提供的脚本激活
source activate_venv.sh

# 安装依赖
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple 
```

### 同步依赖文件

项目提供了 `sync_req.py` 工具，用于从 `pyproject.toml` 生成 `requirements.txt`：

```bash
# 生成 requirements.txt
python sync_req.py

# 使用生成的 requirements.txt 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
```

### 使用说明

👉 直接 `cd` 进对应目录，`python xxx.py -h` 即可开玩！
