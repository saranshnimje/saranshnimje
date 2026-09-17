#!/usr/bin/env python3
"""
Generate a recognizable ASCII portrait SVG from a processed photo.
Creates both animated and static versions.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    sys.exit(1)

# Dense-to-light ramp. Dark pixels use dense characters.
RAMP = "@%#*+=-:. `"
BG_COLOR = "#0d1117"
TEXT_COLOR = "#c9d1d9"


def image_to_ascii(image_path: str, width: int = 100) -> list[str]:
    """Convert an image to ASCII while preserving its prepared aspect ratio."""
    img = Image.open(image_path).convert("L")

    # The preparation step already compensates for terminal character height.
    # Do NOT apply a second 0.5 height correction here; that was squashing faces.
    original_width, original_height = img.size
    if original_width != width:
        height = max(1, round(original_height * width / original_width))
        img = img.resize((width, height), Image.Resampling.LANCZOS)

    # Improve tonal separation so facial features survive ASCII quantization.
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.25)

    ascii_lines: list[str] = []
    levels = len(RAMP) - 1
    for y in range(img.height):
        line = []
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            # Dark = dense character, bright = sparse character.
            index = round((255 - pixel) / 255 * levels)
            index = max(0, min(index, levels))
            line.append(RAMP[index])
        ascii_lines.append("".join(line).rstrip())

    return ascii_lines


def _svg_header(svg_width: int, svg_height: int, animated: bool) -> str:
    description = (
        "Terminal-style ASCII art portrait with row-by-row reveal animation"
        if animated else
        "Terminal-style ASCII art portrait"
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>ASCII portrait</title>
  <desc>{description}</desc>
  <rect width="100%" height="100%" fill="{BG_COLOR}"/>
  <g font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="14" fill="{TEXT_COLOR}" xml:space="preserve">
'''


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_animated_svg(ascii_lines: list[str], output_path: str) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    num_rows = len(ascii_lines)
    max_line_len = max((len(line) for line in ascii_lines), default=80)
    char_width = 8.4
    char_height = 16
    padding = 20
    svg_width = int(max_line_len * char_width + padding * 2)
    svg_height = int(num_rows * char_height + padding * 2)

    svg_content = _svg_header(svg_width, svg_height, True)
    for i, line in enumerate(ascii_lines):
        y = padding + 14 + i * char_height
        delay = i * 0.015
        clip_id = f"clip-row-{i}"
        line_width = max(1, len(line)) * char_width
        svg_content += f'''    <defs>
      <clipPath id="{clip_id}">
        <rect x="{padding}" y="{y - char_height + 4}" width="0" height="{char_height + 2}">
          <animate attributeName="width" from="0" to="{line_width + 10}" dur="0.18s" begin="{delay:.3f}s" fill="freeze"/>
        </rect>
      </clipPath>
    </defs>
    <text x="{padding}" y="{y}" clip-path="url(#{clip_id})">{_escape(line)}</text>
'''

    svg_content += "  </g>\n</svg>"
    output_path.write_text(svg_content, encoding="utf-8")
    return str(output_path)


def generate_static_svg(ascii_lines: list[str], output_path: str) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    num_rows = len(ascii_lines)
    max_line_len = max((len(line) for line in ascii_lines), default=80)
    char_width = 8.4
    char_height = 16
    padding = 20
    svg_width = int(max_line_len * char_width + padding * 2)
    svg_height = int(num_rows * char_height + padding * 2)

    svg_content = _svg_header(svg_width, svg_height, False)
    for i, line in enumerate(ascii_lines):
        y = padding + 14 + i * char_height
        svg_content += f'    <text x="{padding}" y="{y}">{_escape(line)}</text>\n'

    svg_content += "  </g>\n</svg>"
    output_path.write_text(svg_content, encoding="utf-8")
    return str(output_path)


def generate_ascii_portrait(
    image_path: str,
    animated_output: str | None = None,
    static_output: str | None = None,
    width: int = 100,
) -> tuple[str, str]:
    """Generate animated and static ASCII portrait SVGs."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if animated_output is None:
        animated_output = image_path.parent.parent / "assets" / "ascii" / "portrait.svg"
    if static_output is None:
        static_output = image_path.parent.parent / "assets" / "ascii" / "portrait-static.svg"

    print(f"Converting image to ASCII (width={width})...")
    ascii_lines = image_to_ascii(str(image_path), width)

    print("Generating animated SVG...")
    animated_path = generate_animated_svg(ascii_lines, animated_output)
    print(f"Saved: {animated_path}")

    print("Generating static SVG...")
    static_path = generate_static_svg(ascii_lines, static_output)
    print(f"Saved: {static_path}")

    return animated_path, static_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_ascii_svg.py <processed-image.png> [animated.svg] [static.svg] [width]")
        print("  width: ASCII width in characters (default: 100)")
        sys.exit(1)

    input_file = sys.argv[1]
    anim_file = sys.argv[2] if len(sys.argv) > 2 else None
    static_file = sys.argv[3] if len(sys.argv) > 3 else None
    ascii_width = int(sys.argv[4]) if len(sys.argv) > 4 else 100

    generate_ascii_portrait(input_file, anim_file, static_file, ascii_width)
    print("\nDone!")
