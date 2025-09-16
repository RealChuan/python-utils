# -*- coding: utf-8 -*-
from typing import Tuple, Optional
from PIL import Image


def parse_hex_color(hex_color: str) -> Tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    n = len(hex_color)
    if n == 3:
        hex_color = "".join(c * 2 for c in hex_color) + "FF"
    elif n == 4:
        hex_color = "".join(c * 2 for c in hex_color)
    elif n == 6:
        hex_color += "FF"
    elif n != 8:
        raise ValueError("颜色格式错误，支持：#RGB、#RGBA、#RRGGBB、#RRGGBBAA")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6))


def square_image(
    img: Image.Image, bg_color: Optional[Tuple[int, int, int, int]] = None
) -> Image.Image:
    if img.width == img.height:
        return img.copy()
    side = max(img.width, img.height)
    canvas = Image.new("RGBA", (side, side), bg_color or (0, 0, 0, 0))
    x, y = (side - img.width) // 2, (side - img.height) // 2
    canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)
    return canvas
