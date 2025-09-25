# Python Utils

-   [Simplified Chinese](README.md)
-   [English](README.en.md)

Collection of gadgets that make development and life happier 🧰

## 📦 Tool list

| Module            | describe                                                                           | Main Documents                                                                                                                                                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **cli_logger**    | loguru log configuration example, console + file dual channel output               | [`cli_logger.py`](cli_logger/cli_logger.py)                                                                                                                                                                                      |
| **youwatch**      | Real-time monitoring of folder changes (add/delete/modify/rename)                  | [`dirwatch.py`](dirwatch/dirwatch.py)                                                                                                                                                                                            |
| **format_cmake**  | Format CMake files (single or recursive directories)                               | [`format_cmake.py`](format_cmake/format_cmake.py)                                                                                                                                                                                |
| **hash**          | Calculate the hash value of a file or text (MD5/SHA-1/SHA-2/SHA-3/BLAKE2/BLAKE3)   | [`hash.py`](hash/hash.py)                                                                                                                                                                                                        |
| **image-toolkit** | Image format conversion tool + one-click generation/analysis`.icns`/`.ico`         | [`convert_img.py`](image-toolkit/convert_img.py)/[`dump_icns.py`](image-toolkit/dump_icns.py)/[`dump_ico.py`](image-toolkit/dump_ico.py)/[`make_icns.py`](image-toolkit/make_icns.py)/[`make_ico.py`](image-toolkit/make_ico.py) |
| **m3u8_download** | m3u8 downloader, automatically merge ts into a single video                        | [`m3u8_dl.py`](m3u8_download/m3u8_dl.py)                                                                                                                                                                                         |
| **Procmon**       | Real-time monitoring of CPU/memory/thread/handle by process name                   | [`procmon.py`](procmon/procmon.py)                                                                                                                                                                                               |
| **resolve**       | Domain name resolution tool to quickly obtain IP, port, and protocol information   | [`resolve.py`](resolve/resolve.py)                                                                                                                                                                                               |
| **tree**          | Visual directory tree generation tool                                              | [`tree.py`](tree/tree.py)                                                                                                                                                                                                        |
| **utils**         | General Tool Library (Color Output, etc.)                                          | [`colors.py`](utils/colors.py)                                                                                                                                                                                                   |
| **sync_req**      | Relying on the synchronization tool, generate requirements.txt from pyproject.toml | [`sync_req.py`](sync_req.py)                                                                                                                                                                                                     |

## 🚀 Quick start

### Installation dependencies

Recommended use of virtual environments:

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

### Synchronize dependency files

Project provided`sync_req.py`Tools for`pyproject.toml`generate`requirements.txt`：

```bash
# 生成 requirements.txt
python sync_req.py

# 使用生成的 requirements.txt 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
```

### Instructions for use

👉 Direct`cd`Enter the corresponding directory,`python xxx.py -h`You can start playing!
