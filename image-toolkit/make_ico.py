# -*- coding: utf-8 -*-
"""
make_ico.py
将任意图片快速生成多尺寸 ico 图标。

用法:
    ./make_ico.py input.png                    # 透明背景
    ./make_ico.py input.jpg "#FF00FF"          # 指定背景色
    ./make_ico.py input.tiff -o MyIcon.ico    # 指定输出文件名
"""
import os
import sys
import argparse
from PIL import Image
from icon_common import parse_hex_color, square_image

# 常用 ico 尺寸（Windows 推荐倒序存放）
# Pillow 还是会从小到大生成，无视传入的顺序
ICO_SIZES = [256, 128, 64, 48, 32, 24, 16]


def build_ico(source_img: Image.Image, output_ico: str, use_bmp: bool = False) -> None:
    """生成 .ico 文件"""

    icons = []
    for size in ICO_SIZES:
        icons.append(source_img.resize((size, size), Image.LANCZOS))

    save_kw = {
        "format": "ICO",
        "sizes": [(s, s) for s in ICO_SIZES],
        "append_images": icons[1:],
    }
    if use_bmp:  # 只有用户显式要求才加
        save_kw["bitmap_format"] = "bmp"

    icons[0].save(output_ico, **save_kw)
    fmt = "BMP" if use_bmp else "PNG"
    print(f"✅ 已生成 -> {output_ico}（{fmt} 压缩，含尺寸：{ICO_SIZES}）")


def main(argv=None):
    parser = argparse.ArgumentParser(description="把任意图片做成 ico 图标")
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("bgcolor", nargs="?", help="背景色（十六进制，可选，默认透明）")
    parser.add_argument("-o", "--output", help="输出 .ico 文件名（可选）")
    parser.add_argument(
        "--bmp",
        action="store_true",
        help="用 BMP 帧写入 ICO：无压缩、体积大，但 Windows 资源查看器“属性-详细信息”页可立即显示前五帧里最大的尺寸。",
    )
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
        out_ico = args.output
    else:
        base, _ = os.path.splitext(args.input)
        out_ico = base + ".ico"

    # 5. 生成 ico
    build_ico(square, out_ico, use_bmp=args.bmp)  # 把开关传进去


if __name__ == "__main__":
    main()
