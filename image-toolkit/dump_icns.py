# -*- coding: utf-8 -*-
"""
dump_icns.py
读取 .icns 文件并导出所有图片

用法:
    ./dump_icns.py app.icns              # 仅打印信息
    ./dump_icns.py app.icns -s           # 同时导出 PNG
"""
import os
import sys
import argparse
from PIL import Image, IcnsImagePlugin


def icns_frames(icns_path: str):
    """
    返回 [( (w,h,scale), bpp, Image ), ... ]
    注意：Pillow 只能读到“含 PNG/JPEG2000 数据”的条目；
    缺失的 (16,16,1)、(32,32,1) 等可用
        iconutil -c iconset xxx.icns -o xxx.iconset
    解包后拿到全套 PNG，再单独处理。
    """
    frames = []
    with open(icns_path, "rb") as fp:
        icn = IcnsImagePlugin.IcnsFile(fp)

        sizes = list(icn.itersizes())
        # ---------- 注意 ----------
        need = {(16, 16, 1), (32, 32, 1)}
        missing = need - set(sizes)
        if missing:
            print("⚠️  Pillow 无法解析以下传统格式条目（无 PNG 块）：", *missing)
        # ----------------------------
        # 所有可用尺寸 (w, h, scale)
        for size in sizes:
            img = icn.getimage(size).copy()  # 原始分辨率，无需 resize
            bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32}.get(img.mode, 32)
            frames.append((size, bpp, img))
    return frames


def save_all(icns_path: str, do_save: bool):
    frames = icns_frames(icns_path)
    print(f"共找到 {len(frames)} 张图片：")

    max_w = max(
        len(f"{w}x{h}{'@' + str(s) + 'x' if s > 1 else ''}")
        for (w, h, s), _, _ in frames
    )

    out_dir = os.path.splitext(icns_path)[0] if do_save else None
    if do_save:
        os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.basename(out_dir) if do_save else ""

    for idx, ((w, h, scale), bpp, img) in enumerate(frames, 1):
        retina = f"@{scale}x" if scale > 1 else ""
        size_str = f"{w}x{h}{retina}"
        print(f"  {idx:>2}. {size_str:<{max_w}}  {bpp:>2}-bit", end="")

        if do_save:
            png_path = os.path.join(out_dir, f"{base_name}_{w}x{h}{retina}.png")
            img.save(png_path)
            print(f"    已导出 -> {png_path}")
        else:
            print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="用 Pillow 内部 API 提取 ICNS 所有原始帧"
    )
    parser.add_argument("icns", help="输入 .icns 文件")
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="将各尺寸保存为 PNG（保存在 icns 同名目录）",
    )
    args = parser.parse_args(argv)

    if not os.path.isfile(args.icns):
        sys.exit("输入文件不存在")
    if os.path.splitext(args.icns)[1].lower() != ".icns":
        sys.exit("请输入扩展名为 .icns 的文件")

    save_all(args.icns, args.save)


if __name__ == "__main__":
    main()
