"""The app icon, drawn in pure Python, and the colour arithmetic the schemes are checked with.

star_mark rasterizes the four-point star from signed distances and encodes
it as PNG with an alpha channel; encode_ico packs the sizes Windows asks for
(packaging/make_icon.py writes Cynosure.ico). mix and contrast are the colour
sums theme.Colors and the contrast tests use. Pillow is not needed: the
encoder is zlib and struct from the standard library.
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


def _segment_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    if length <= 0.0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))



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
