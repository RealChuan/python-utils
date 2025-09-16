#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make-icns.py
在 macOS 下把任意图片做成 .icns 图标并自动用系统预览打开。

用法:
    ./make-icns.py input.png                    # 透明背景
    ./make-icns.py input.jpg "#FF00FF"          # 指定背景色
    ./make-icns.py input.tiff -o MyIcon.icns    # 指定输出文件名
"""
import os
import sys
import argparse
import tempfile
import subprocess
from PIL import Image, ImageOps

# icns 所需全部分辨率
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def parse_hex_color(hex_color: str):
    """
    支持 #RGB、#RGBA、#RRGGBB、#RRGGBBAA
    返回 (R, G, B, A)  0-255
    """
    hex_color = hex_color.lstrip("#")
    n = len(hex_color)
    if n == 3:  # #RGB   -> #RRGGBB + 不透明
        hex_color = "".join(c * 2 for c in hex_color) + "FF"
    elif n == 4:  # #RGBA  -> #RRGGBBAA
        hex_color = "".join(c * 2 for c in hex_color)
    elif n == 6:  # #RRGGBB -> 不透明
        hex_color += "FF"
    elif n != 8:
        raise ValueError("颜色格式错误，支持：#RGB、#RGBA、#RRGGBB、#RRGGBBAA")

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6))


def square_image(img: Image.Image, bg_color=None) -> Image.Image:
    """将 img 做成最小外接正方形，bg_color=None 代表透明"""
    if img.width == img.height:
        return img.copy()
    side = max(img.width, img.height)
    if bg_color is None:  # 透明
        new_im = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    else:  # 纯色
        new_im = Image.new("RGBA", (side, side), bg_color)
    # 居中粘贴
    x = (side - img.width) // 2
    y = (side - img.height) // 2
    new_im.paste(img, (x, y), img if img.mode == "RGBA" else None)
    return new_im


def build_icns(source_img: Image.Image, output_icns: str):
    """生成 .icns 文件"""
    tempdir = tempfile.mkdtemp()
    iconset = os.path.join(tempdir, "Icon.iconset")
    os.makedirs(iconset)

    for size in ICNS_SIZES:
        # 1× 和 2×  Retina 版本
        for scale, suffix in [(1, ""), (2, "@2x")]:
            px = size * scale
            img_scaled = source_img.resize((px, px), Image.LANCZOS)
            filename = f"icon_{size}x{size}{suffix}.png"
            img_scaled.save(os.path.join(iconset, filename))

    # 调用系统 iconutil 生成 icns
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", output_icns], check=True)
    # 清理
    subprocess.run(["rm", "-rf", tempdir])


def open_in_viewer(path: str):
    """用 macOS 默认的 icns 查看器（Preview）打开"""
    subprocess.run(["open", path])


def main():
    parser = argparse.ArgumentParser(description="把任意图片做成 macOS .icns 图标")
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("bgcolor", nargs="?", help="背景色（十六进制，可选，默认透明）")
    parser.add_argument("-o", "--output", help="输出 .icns 文件名（可选）")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit("输入文件不存在")

    # 1. 读图
    img = Image.open(args.input).convert("RGBA")

    # 2. 背景色
    if args.bgcolor:
        bg_color = parse_hex_color(args.bgcolor)
    else:
        bg_color = None  # 透明

    # 3. 正方形化
    square = square_image(img, bg_color)

    # 4. 输出文件名
    if args.output:
        out_icns = args.output
    else:
        base, _ = os.path.splitext(args.input)
        out_icns = base + ".icns"

    # 5. 生成 icns
    build_icns(square, out_icns)
    print("已生成 →", out_icns)

    # 6. 打开查看
    open_in_viewer(out_icns)


if __name__ == "__main__":
    main()
