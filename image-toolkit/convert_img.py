# -*- coding: utf-8 -*-
"""
convert_img.py
通用图片格式/分辨率批量转换工具

用法:
    ./convert_img.py input.png
    ./convert_img.py input.png -f webp -r 800x600
    ./convert_img.py input.png -r 1920x1080 --no-ratio -q 90
    ./convert_img.py --list-input
    ./convert_img.py --list-output
"""
import os
import sys
import datetime
import argparse
from PIL import Image, ImageOps


# -------------------- 列表格式 --------------------
def list_input_formats():
    """Pillow 能读取的格式"""
    return sorted(
        {
            ext.lstrip(".").lower()
            for ext, fmt in Image.registered_extensions().items()
            if fmt in Image.OPEN
        }
    )


def list_output_formats():
    """Pillow 能写入的格式"""
    return sorted(
        {
            ext.lstrip(".").lower()
            for ext, fmt in Image.registered_extensions().items()
            if fmt in Image.SAVE
        }
    )


# -------------------- 分辨率解析 --------------------
def parse_resolution(s: str):
    try:
        w, h = map(int, s.lower().split("x"))
        return w, h
    except Exception:
        raise argparse.ArgumentTypeError("分辨率格式必须是 宽x高，例如 800x600")


# -------------------- 核心转换 --------------------
def convert_image(
    src_path, dst_template: str, dst_size=None, keep_ratio=True, quality=95
):
    """
    :param dst_template: 带 {} 占位符的路径模板，例如
                         '/tmp/demo_20250920_{}x{}.webp'
    """
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im).convert("RGBA")

        # 1. 缩放并拿到真实分辨率
        if dst_size:
            src_w, src_h = im.size
            dst_w, dst_h = dst_size
            if keep_ratio:
                ratio = min(dst_w / src_w, dst_h / src_h)
                dst_w, dst_h = int(src_w * ratio), int(src_h * ratio)
            im = im.resize((dst_w, dst_h), Image.LANCZOS)
        else:
            dst_w, dst_h = im.size  # 未指定分辨率就用原图尺寸

        # 2. 生成最终路径
        dst_path = dst_template.format(dst_w, dst_h)

        # 3. 保存
        save_kw = {}
        ext = os.path.splitext(dst_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            im = im.convert("RGB")
            save_kw.update(quality=quality, optimize=True)
        elif ext == ".webp":
            save_kw.update(quality=quality)
        elif ext == ".png":
            save_kw.update(optimize=True)

        im.save(dst_path, **save_kw)
        print(f"✅ 已生成 -> {dst_path}")


# -------------------- 命令行入口 --------------------
def main(argv=None):
    parser = argparse.ArgumentParser(description="万能图片转换小工具")
    parser.add_argument("input", nargs="?", help="输入图片路径")
    parser.add_argument(
        "-f", "--format", help="输出格式（jpg/png/bmp/webp/...），默认保持原格式"
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=parse_resolution,
        help="目标分辨率 宽x高，例如 800x600",
    )
    parser.add_argument(
        "--no-ratio", action="store_true", help="不保持宽高比（默认保持）"
    )
    parser.add_argument("-o", "--output", help="输出目录（默认跟输入图片同目录）")
    parser.add_argument(
        "-q", "--quality", type=int, default=95, help="JPEG/WebP 质量，默认 95"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--list-input", action="store_true", help="列出本脚本支持的所有输入格式"
    )
    group.add_argument(
        "--list-output", action="store_true", help="列出本脚本支持的所有输出格式"
    )

    args = parser.parse_args(argv)

    # ---- 列表模式 ----
    if args.list_input:
        print("本脚本支持的输入格式：")
        print(" ".join(list_input_formats()))
        return
    if args.list_output:
        print("本脚本支持的输出格式：")
        print(" ".join(list_output_formats()))
        return

    # ---- 转换模式 ----
    if not args.input:
        parser.print_help()
        sys.exit("请提供输入文件，或使用 --list-input / --list-output 查看支持格式")
    if not os.path.isfile(args.input):
        sys.exit("输入文件不存在")

    out_dir = args.output or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(out_dir, exist_ok=True)

    src_ext = os.path.splitext(args.input)[1][1:].lower()
    dst_ext = (args.format or src_ext).lower().strip(".")
    if dst_ext == "jpeg":
        dst_ext = "jpg"

    date_str = datetime.datetime.now().strftime("%Y%m%d")
    dst_template = os.path.join(
        out_dir,
        f"{os.path.splitext(os.path.basename(args.input))[0]}_{date_str}_{{}}x{{}}.{dst_ext}",
    )

    convert_image(
        args.input,
        dst_template,
        dst_size=args.resolution,
        keep_ratio=not args.no_ratio,
        quality=args.quality,
    )


if __name__ == "__main__":
    main()
