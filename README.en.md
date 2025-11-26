# Python Utils

-   [Simplified Chinese](README.md)
-   [English](README.en.md)

A collection of gadgets that make development and life happier 🧰

## 📦 Tool list

| module            | describe                                                                             | main document                                                                                                                                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **cli_logger**    | Loguru log configuration example, console + file dual-channel output                 | [`cli_logger.py`](src/cli_logger/cli_logger.py)                                                                                                                                                                                                      |
| **youwatch**      | Real-time monitoring of folder changes (add/delete/modify/rename)                    | [`dirwatch.py`](src/dirwatch/dirwatch.py)                                                                                                                                                                                                            |
| **format_cmake**  | Format CMake files (single or recursive directories)                                 | [`format_cmake.py`](src/format_cmake/format_cmake.py)                                                                                                                                                                                                |
| **hash**          | Calculate the hash value of a file or text (MD5/SHA-1/SHA-2/SHA-3/BLAKE2/BLAKE3)     | [`hash.py`](src/hash/hash.py)                                                                                                                                                                                                                        |
| **image-toolkit** | Image format conversion tool + one-click generation/analysis`.icns`/`.ico`           | [`convert_img.py`](src/image-toolkit/convert_img.py)/[`dump_icns.py`](src/image-toolkit/dump_icns.py)/[`dump_ico.py`](src/image-toolkit/dump_ico.py)/[`make_icns.py`](src/image-toolkit/make_icns.py)/[`make_ico.py`](src/image-toolkit/make_ico.py) |
| **m3u8_download** | m3u8 downloader, automatically merge ts into a single video                          | [`m3u8_dl.py`](src/m3u8_download/m3u8_dl.py)                                                                                                                                                                                                         |
| **procmon**       | Real-time monitoring of CPU/memory/threads/handles by process name                   | [`procmon.py`](src/procmon/procmon.py)                                                                                                                                                                                                               |
| **resolve**       | Domain name resolution tool to quickly obtain IP, port, and protocol information     | [`resolve.py`](src/resolve/resolve.py)                                                                                                                                                                                                               |
| **tree**          | Visual directory tree generation tool                                                | [`tree.py`](src/tree/tree.py)                                                                                                                                                                                                                        |
| **utils**         | General tool library (color output, etc.)                                            | [`colors.py`](src/utils/colors.py)                                                                                                                                                                                                                   |
| **sync_req**      | Depend on the synchronization tool and generate requirements.txt from pyproject.toml | [`sync_req.py`](sync_req.py)                                                                                                                                                                                                                         |

## 🚀 Quick start

### Install uv

First you need to install uv - the extremely fast Python package manager and project tool chain:

**Install using pip (cross-platform):**

```bash
pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Verify installation:**

```bash
uv --version
```

### Install project dependencies

Use uv to manage project dependencies:

```bash
# 使用 uv 创建虚拟环境并安装所有依赖（一步完成）
uv sync --dev

# 或者分步执行：
# 1. 创建虚拟环境（默认在 .venv 目录）
uv venv

# 2. 激活虚拟环境 (Linux/macOS)
source .venv/bin/activate

# 3. 安装项目依赖（可编辑模式）
uv pip install -e .
```

### Synchronize dependency files

The project provides`sync_req.py`Tools for starting from`pyproject.toml`generate`requirements.txt`：

```bash
# 生成 requirements.txt
python sync_req.py

# 使用 uv 通过 requirements.txt 安装依赖
uv pip install -r requirements.txt
```

### Use Tsinghua image acceleration (optional)

If you need to use domestic mirror sources:

```bash
# 设置环境变量使用清华镜像
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
uv sync --dev

# 或者单次命令指定镜像
uv pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Instructions for use

👉 Direct`cd`Enter the corresponding directory,`uv run python xxx.py -h`Check out the specific usage!
