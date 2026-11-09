"""Anti-aliased shapes as PNG bytes, drawn in pure Python.

tkinter has no rounded corners and its canvas does not smooth an edge. The
window's rounded buttons, fields, cards, scrollbar thumbs, check boxes, and
small icons are therefore pictures: this module rasterizes them from signed
distance functions and encodes them as PNG with an alpha channel, which Tk 8.6
reads natively. theme.py turns the bytes into ttk image elements that stretch
by nine slices, so one small picture serves a control of any size.

Nothing here imports tkinter, so the tests can check a shape without a display.
Pillow is not needed: the encoder is zlib and struct from the standard library.
"""

from __future__ import annotations

import math
import struct
import zlib

Color = tuple[int, int, int]


def parse_color(value: str) -> Color:
    """#rgb or #rrggbb to an (r, g, b) tuple."""
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"not a hex colour: {value!r}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def to_hex(color: Color) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(part)))) for part in color)


def mix(first: str, second: str, share: float) -> str:
    """share of first over second, as CSS color-mix(in srgb, first share, second) does."""
    share = max(0.0, min(1.0, share))
    a, b = parse_color(first), parse_color(second)
    return to_hex(tuple(a[i] * share + b[i] * (1.0 - share) for i in range(3)))


def _linear(channel: int) -> float:
    value = channel / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    """WCAG relative luminance."""
    r, g, b = parse_color(color)
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast(first: str, second: str) -> float:
    """WCAG contrast ratio between two colours, 1.0 to 21.0."""
    a, b = luminance(first), luminance(second)
    lighter, darker = (a, b) if a >= b else (b, a)
    return (lighter + 0.05) / (darker + 0.05)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, pixels: bytes | bytearray) -> bytes:
    """RGBA bytes, row by row from the top, as a PNG file."""
    if width <= 0 or height <= 0:
        raise ValueError("a PNG needs a positive width and height")
    if len(pixels) != width * height * 4:
        raise ValueError("pixel data does not match the size")
    stride = width * 4
    raw = bytearray()
    for row in range(height):
        raw.append(0)  # filter type none
        raw += pixels[row * stride:(row + 1) * stride]
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


def png_size(data: bytes) -> tuple[int, int]:
    """Width and height from a PNG header."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def decode_png(data: bytes) -> tuple[int, int, bytes]:
    """Read back a PNG written by encode_png. Used by the tests."""
    width, height = png_size(data)
    position = 8
    body = b""
    while position < len(data):
        (length,) = struct.unpack(">I", data[position:position + 4])
        kind = data[position + 4:position + 8]
        if kind == b"IDAT":
            body += data[position + 8:position + 8 + length]
        position += 12 + length
    raw = zlib.decompress(body)
    stride = width * 4
    pixels = bytearray()
    for row in range(height):
        start = row * (stride + 1)
        if raw[start] != 0:
            raise ValueError("only unfiltered rows are read back")
        pixels += raw[start + 1:start + 1 + stride]
    return width, height, bytes(pixels)


def _coverage(distance: float) -> float:
    """Share of a pixel inside an edge whose signed distance at the pixel centre is distance."""
    return max(0.0, min(1.0, 0.5 - distance))


def _box_distance(x: float, y: float, half_w: float, half_h: float, radius: float) -> float:
    """Signed distance from (x, y), measured from the box centre, to a rounded box."""
    qx = abs(x) - (half_w - radius)
    qy = abs(y) - (half_h - radius)
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    inside = min(max(qx, qy), 0.0)
    return outside + inside - radius


def _corner_radii(radius, width: int, height: int) -> tuple[float, float, float, float]:
    """(top-left, top-right, bottom-right, bottom-left), each kept inside the box."""
    if isinstance(radius, (int, float)):
        radii = (float(radius),) * 4
    else:
        radii = tuple(float(value) for value in radius)
        if len(radii) != 4:
            raise ValueError("radius is one number or four, clockwise from the top left")
    limit = min(width, height) / 2.0
    return tuple(max(0.0, min(value, limit)) for value in radii)


def rounded_rect(
    width: int,
    height: int,
    radius,
    fill: str | None,
    *,
    border: str | None = None,
    border_width: float = 1.0,
    fill_alpha: float = 1.0,
) -> bytes:
    """A rounded rectangle with an optional border line, as PNG bytes.

    radius is one number, or four clockwise from the top left for a box whose
    corners differ. fill None leaves the inside clear, which draws a ring.
    """
    radii = _corner_radii(radius, width, height)
    fill_rgb = parse_color(fill) if fill else (0, 0, 0)
    border_rgb = parse_color(border) if border else fill_rgb
    inset = float(border_width) if border else 0.0
    half_w, half_h = width / 2.0, height / 2.0
    # With four equal corners the picture is the same in every quarter, so one is drawn.
    uniform = len(set(radii)) == 1
    rows = (height + 1) // 2 if uniform else height
    columns = (width + 1) // 2 if uniform else width
    pixels = bytearray(width * height * 4)
    for row in range(rows):
        y = row + 0.5 - half_h
        for column in range(columns):
            x = column + 0.5 - half_w
            # Quarter: 0 top-left, 1 top-right, 2 bottom-right, 3 bottom-left.
            quarter = (0 if x < 0 else 1) if y < 0 else (3 if x < 0 else 2)
            r_outer = radii[quarter]
            outer = _coverage(_box_distance(x, y, half_w, half_h, r_outer))
            if outer <= 0.0:
                continue
            if inset > 0.0:
                r_inner = max(0.0, r_outer - inset)
                inner = _coverage(_box_distance(x, y, half_w - inset, half_h - inset, r_inner))
            else:
                inner = outer
            fill_part = inner * (fill_alpha if fill else 0.0)
            ring = max(0.0, outer - inner) if border else 0.0
            alpha = ring + fill_part
            if alpha <= 0.0:
                continue
            value = (
                max(0, min(255, int(round((border_rgb[0] * ring + fill_rgb[0] * fill_part) / alpha)))),
                max(0, min(255, int(round((border_rgb[1] * ring + fill_rgb[1] * fill_part) / alpha)))),
                max(0, min(255, int(round((border_rgb[2] * ring + fill_rgb[2] * fill_part) / alpha)))),
                max(0, min(255, int(round(alpha * 255)))),
            )
            spots = [(row, column)]
            if uniform:
                spots += [
                    (row, width - 1 - column),
                    (height - 1 - row, column),
                    (height - 1 - row, width - 1 - column),
                ]
            for spot_row, spot_column in spots:
                offset = (spot_row * width + spot_column) * 4
                pixels[offset:offset + 4] = bytes(value)
    return encode_png(width, height, pixels)


def _segment_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    if length <= 0.0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def strokes(
    size: int,
    lines: list[tuple[float, float, float, float]],
    color: str,
    *,
    width: float = 1.6,
    dots: list[tuple[float, float, float]] | None = None,
    canvas: tuple[int, int] | None = None,
) -> bytes:
    """Round-capped line segments and filled dots on a clear square, as PNG bytes.

    Coordinates are fractions of size, so one drawing serves every display
    scale. dots are (x, y, radius) in the same fractions.
    """
    w, h = canvas or (size, size)
    rgb = parse_color(color)
    half = width / 2.0
    segments = [(a * size, b * size, c * size, d * size) for a, b, c, d in lines]
    points = [(x * size, y * size, r * size) for x, y, r in (dots or [])]
    pixels = bytearray(w * h * 4)
    for row in range(h):
        y = row + 0.5
        for column in range(w):
            x = column + 0.5
            best = 0.0
            for ax, ay, bx, by in segments:
                best = max(best, _coverage(_segment_distance(x, y, ax, ay, bx, by) - half))
                if best >= 1.0:
                    break
            for cx, cy, radius in points:
                best = max(best, _coverage(math.hypot(x - cx, y - cy) - radius))
            if best <= 0.0:
                continue
            offset = (row * w + column) * 4
            pixels[offset], pixels[offset + 1], pixels[offset + 2] = rgb
            pixels[offset + 3] = int(round(best * 255))
    return encode_png(w, h, pixels)


def disc(size: int, color: str, *, radius: float | None = None, alpha: float = 1.0) -> bytes:
    """A filled circle centred on a clear square."""
    rgb = parse_color(color)
    radius = size / 2.0 if radius is None else radius
    centre = size / 2.0
    pixels = bytearray(size * size * 4)
    for row in range(size):
        for column in range(size):
            cover = _coverage(math.hypot(column + 0.5 - centre, row + 0.5 - centre) - radius)
            if cover <= 0.0:
                continue
            offset = (row * size + column) * 4
            pixels[offset], pixels[offset + 1], pixels[offset + 2] = rgb
            pixels[offset + 3] = int(round(cover * alpha * 255))
    return encode_png(size, size, pixels)


def overlay(base: bytes, top: bytes) -> bytes:
    """top drawn over base, both the same size. Used for a check mark on its box."""
    width, height, under = decode_png(base)
    top_width, top_height, over = decode_png(top)
    if (width, height) != (top_width, top_height):
        raise ValueError("overlay needs two pictures of one size")
    out = bytearray(under)
    for offset in range(0, len(out), 4):
        alpha = over[offset + 3] / 255.0
        if alpha <= 0.0:
            continue
        under_alpha = out[offset + 3] / 255.0
        total = alpha + under_alpha * (1.0 - alpha)
        for channel in range(3):
            value = (over[offset + channel] * alpha + out[offset + channel] * under_alpha * (1.0 - alpha)) / total
            out[offset + channel] = max(0, min(255, int(round(value))))
        out[offset + 3] = max(0, min(255, int(round(total * 255))))
    return encode_png(width, height, out)


def extend(data: bytes, *, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0) -> bytes:
    """The picture with clear margins added. A margin is how an image element gets its spacing."""
    width, height, pixels = decode_png(data)
    new_width, new_height = width + left + right, height + top + bottom
    out = bytearray(new_width * new_height * 4)
    for row in range(height):
        start = ((row + top) * new_width + left) * 4
        out[start:start + width * 4] = pixels[row * width * 4:(row + 1) * width * 4]
    return encode_png(new_width, new_height, out)


def clear(width: int = 1, height: int = 1) -> bytes:
    """A fully transparent picture."""
    return encode_png(width, height, bytearray(width * height * 4))


# Icon drawings: line segments in fractions of the icon box.
ICONS: dict[str, dict] = {
    "check": {"lines": [(0.22, 0.54, 0.42, 0.72), (0.42, 0.72, 0.78, 0.30)]},
    "chevron_down": {"lines": [(0.28, 0.40, 0.50, 0.62), (0.50, 0.62, 0.72, 0.40)]},
    "chevron_right": {"lines": [(0.40, 0.28, 0.62, 0.50), (0.62, 0.50, 0.40, 0.72)]},
    "arrow_up": {"lines": [(0.50, 0.78, 0.50, 0.24), (0.27, 0.46, 0.50, 0.23), (0.73, 0.46, 0.50, 0.23)]},
    "plus": {"lines": [(0.50, 0.22, 0.50, 0.78), (0.22, 0.50, 0.78, 0.50)]},
    "close": {"lines": [(0.28, 0.28, 0.72, 0.72), (0.72, 0.28, 0.28, 0.72)]},
    "more": {"lines": [], "dots": [(0.22, 0.50, 0.075), (0.50, 0.50, 0.075), (0.78, 0.50, 0.075)]},
    "stop": {"lines": [(0.34, 0.34, 0.66, 0.34), (0.66, 0.34, 0.66, 0.66), (0.66, 0.66, 0.34, 0.66),
                       (0.34, 0.66, 0.34, 0.34), (0.42, 0.50, 0.58, 0.50), (0.50, 0.42, 0.50, 0.58)]},
    "panel": {"lines": [(0.18, 0.24, 0.82, 0.24), (0.82, 0.24, 0.82, 0.76), (0.82, 0.76, 0.18, 0.76),
                        (0.18, 0.76, 0.18, 0.24), (0.60, 0.24, 0.60, 0.76)]},
}


def icon(name: str, size: int, color: str, *, width: float | None = None) -> bytes:
    """One of ICONS at size pixels, in color."""
    drawing = ICONS[name]
    stroke = width if width is not None else max(1.3, size / 10.0)
    return strokes(size, drawing.get("lines", []), color, width=stroke, dots=drawing.get("dots"))


def star_mark(size: int, fill: str, background: str | None = None, *, radius_share: float = 0.22) -> bytes:
    """The app mark: a four-point star, the guide star the name refers to.

    With background, the star sits on a rounded square of that colour, which
    is the window and installer icon. Without it, the star alone is drawn.
    """
    centre = size / 2.0
    reach = size * (0.36 if background else 0.48)
    waist = reach * 0.20
    star_rgb = parse_color(fill)
    back_rgb = parse_color(background) if background else None
    corner = size * radius_share
    # The star is the union of four kites that meet at the centre.
    tips = [(0.0, -reach), (reach, 0.0), (0.0, reach), (-reach, 0.0)]
    sides = [(waist, -waist), (waist, waist), (-waist, waist), (-waist, -waist)]
    polygon = []
    for index in range(4):
        polygon.append(tips[index])
        polygon.append(sides[index])
    edges = [(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon))]

    def star_distance(x: float, y: float) -> float:
        inside = False
        nearest = float("inf")
        for (ax, ay), (bx, by) in edges:
            nearest = min(nearest, _segment_distance(x, y, ax, ay, bx, by))
            if (ay > y) != (by > y):
                cross = ax + (y - ay) * (bx - ax) / (by - ay)
                if x < cross:
                    inside = not inside
        return -nearest if inside else nearest

    pixels = bytearray(size * size * 4)
    for row in range(size):
        y = row + 0.5 - centre
        for column in range(size):
            x = column + 0.5 - centre
            star = _coverage(star_distance(x, y))
            back = _coverage(_box_distance(x, y, centre, centre, corner)) if back_rgb else 0.0
            alpha = star + back * (1.0 - star)
            if alpha <= 0.0:
                continue
            offset = (row * size + column) * 4
            for channel in range(3):
                under = back_rgb[channel] * back * (1.0 - star) if back_rgb else 0.0
                pixels[offset + channel] = max(0, min(255, int(round((star_rgb[channel] * star + under) / alpha))))
            pixels[offset + 3] = max(0, min(255, int(round(alpha * 255))))
    return encode_png(size, size, pixels)


def _ico_bitmap(data: bytes) -> bytes:
    """One icon picture as the bitmap an .ico file holds: 32-bit colour rows, then a 1-bit mask."""
    width, height, pixels = decode_png(data)
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    colour = bytearray()
    mask = bytearray()
    row_bytes = ((width + 31) // 32) * 4
    for row in range(height - 1, -1, -1):
        bits = bytearray(row_bytes)
        for column in range(width):
            offset = (row * width + column) * 4
            red, green, blue, alpha = pixels[offset:offset + 4]
            colour += bytes((blue, green, red, alpha))
            if alpha == 0:
                bits[column // 8] |= 0x80 >> (column % 8)
        mask += bits
    return header + bytes(colour) + bytes(mask)


def encode_ico(pictures: list[bytes]) -> bytes:
    """PNG pictures of several sizes as one Windows .ico file.

    A picture under 256 pixels is stored as a bitmap, which every Windows
    tool reads. The 256-pixel picture is stored as PNG, as Windows expects.
    """
    entries = []
    for data in pictures:
        width, height = png_size(data)
        body = data if width >= 256 or height >= 256 else _ico_bitmap(data)
        entries.append((width, height, body))
    header = struct.pack("<HHH", 0, 1, len(entries))
    directory = b""
    payload = b""
    offset = 6 + 16 * len(entries)
    for width, height, body in entries:
        directory += struct.pack(
            "<BBBBHHII",
            0 if width >= 256 else width,
            0 if height >= 256 else height,
            0, 0, 1, 32, len(body), offset,
        )
        payload += body
        offset += len(body)
    return header + directory + payload
