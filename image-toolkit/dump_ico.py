# -*- coding: utf-8 -*-
"""
dump_ico.py
读取 .ico 文件并导出所有图片

用法:
    ./dump_ico.py app.ico              # 仅打印信息
    ./dump_ico.py app.ico -s           # 同时导出 PNG
"""
import os
import sys
import argparse
from PIL import Image, IcoImagePlugin


def ico_frames(ico_path: str):
    """返回 [( (w,h), approx_bpp, Image ), ... ]"""
    frames = []
    with open(ico_path, "rb") as fp:
        ico = IcoImagePlugin.IcoFile(fp)
        for w, h in sorted(ico.sizes()):
            idx = ico.getentryindex((w, h))
            img = ico.frame(idx)
            # 用 mode 估算 bpp
            bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32}.get(img.mode, 32)
            frames.append(((w, h), bpp, img))
    return frames


def save_all(ico_path: str, do_save: bool):
    frames = ico_frames(ico_path)
    print(f"共找到 {len(frames)} 张图片：")

    # 预计算列宽，美观对齐
    max_w = max(len(f"{w}x{h}") for (w, h), _, _ in frames)

    out_dir = os.path.splitext(ico_path)[0] if do_save else None
    if do_save:
        os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.basename(out_dir) if do_save else ""

    for idx, (wh, bpp, img) in enumerate(frames, 1):
        w, h = wh
        size_str = f"{w}x{h}"
        # 同一行打印分辨率 + bpp
        print(f"  {idx:>2}. {size_str:<{max_w}}  {bpp:>2}-bit", end="")

        if do_save:
            png_path = os.path.join(out_dir, f"{base_name}_{w}x{h}.png")
            img.save(png_path)
            print(f"    已导出 -> {png_path}")  # 直接输出完整路径
        else:
            print()  # 仅换行


def main(argv=None):
    parser = argparse.ArgumentParser(description="读取并导出 ICO 内所有图片")
    parser.add_argument("ico", help="输入 .ico 文件")
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="将各尺寸保存为 PNG（保存在 ico 同名目录）",
    )
    args = parser.parse_args(argv)

    if not os.path.isfile(args.ico):
        sys.exit("输入文件不存在")
    if os.path.splitext(args.ico)[1].lower() != ".ico":
        sys.exit("请输入扩展名为 .ico 的文件")
    try:
        with Image.open(args.ico) as im:
            if im.format != "ICO":
                raise ValueError
    except Exception:
        sys.exit("文件内容不是有效的 ICO 格式")

    save_all(args.ico, args.save)


if __name__ == "__main__":
    main()
