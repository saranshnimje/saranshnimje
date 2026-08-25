#!/usr/bin/env python3
"""
Generate ASCII portrait SVG from a processed photo.
Creates both animated and static versions.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    sys.exit(1)

# ASCII density ramp (light to dark)
RAMP = " .`:-=+*#%@"

# SVG color scheme
BG_COLOR = "#0d1117"
TEXT_COLOR = "#c9d1d9"


def image_to_ascii(image_path: str, width: int = 80) -> list:
    """
    Convert an image to ASCII characters.
    
    Args:
        image_path: Path to processed image
        width: Output width in characters
    
    Returns:
        List of strings representing ASCII art
    """
    img = Image.open(image_path).convert("L")
    
    # Calculate new dimensions
    original_width, original_height = img.size
    aspect_ratio = original_height / original_width
    height = int(width * aspect_ratio * 0.5)  # Terminal char aspect ratio
    
    # Resize
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert to ASCII
    ascii_lines = []
    for y in range(height):
        line = ""
        for x in range(width):
            # Get pixel value (0-255)
            pixel = img_resized.getpixel((x, y))
            
            # Map to ASCII character
            # Invert: bright pixels = sparse chars, dark pixels = dense chars
            char_index = int((255 - pixel) / 256 * (len(RAMP) - 1))
            char_index = max(0, min(char_index, len(RAMP) - 1))
            line += RAMP[char_index]
        
        ascii_lines.append(line)
    
    return ascii_lines


def generate_animated_svg(ascii_lines: list, output_path: str) -> str:
    """
    Generate an animated SVG where rows appear sequentially.
    
    Args:
        ascii_lines: List of ASCII art strings
        output_path: Path to save SVG
    
    Returns:
        Path to generated SVG
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate dimensions
    num_rows = len(ascii_lines)
    max_line_len = max(len(line) for line in ascii_lines) if ascii_lines else 80
    
    # Character dimensions (monospace font)
    char_width = 8.4
    char_height = 16
    
    padding = 20
    svg_width = int(max_line_len * char_width + padding * 2)
    svg_height = int(num_rows * char_height + padding * 2)
    
    # Start building SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>ASCII portrait</title>
  <desc>Terminal-style ASCII art portrait with row-by-row reveal animation</desc>
  
  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}"/>
  
  <!-- ASCII Art -->
  <g font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="14" fill="{TEXT_COLOR}">
'''
    
    # Add each row with clip-path animation
    for i, line in enumerate(ascii_lines):
        y = padding + 14 + i * char_height
        
        # Escape XML special characters
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Animation: each row reveals from left to right with delay
        delay = i * 0.02  # 20ms per row
        clip_id = f"clip-row-{i}"
        line_width = len(line) * char_width
        
        svg_content += f'''    <!-- Row {i + 1} -->
    <defs>
      <clipPath id="{clip_id}">
        <rect x="0" y="{y - char_height + 4}" width="0" height="{char_height + 2}">
          <animate attributeName="width" from="0" to="{line_width + 10}" dur="0.15s" begin="{delay:.3f}s" fill="freeze"/>
        </rect>
      </clipPath>
    </defs>
    <text x="{padding}" y="{y}" clip-path="url(#{clip_id})">{escaped_line}</text>
'''
    
    svg_content += '''  </g>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return str(output_path)


def generate_static_svg(ascii_lines: list, output_path: str) -> str:
    """
    Generate a static SVG (no animation) as fallback.
    
    Args:
        ascii_lines: List of ASCII art strings
        output_path: Path to save SVG
    
    Returns:
        Path to generated SVG
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate dimensions
    num_rows = len(ascii_lines)
    max_line_len = max(len(line) for line in ascii_lines) if ascii_lines else 80
    
    # Character dimensions (monospace font)
    char_width = 8.4
    char_height = 16
    
    padding = 20
    svg_width = int(max_line_len * char_width + padding * 2)
    svg_height = int(num_rows * char_height + padding * 2)
    
    # Start building SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>ASCII portrait</title>
  <desc>Terminal-style ASCII art portrait</desc>
  
  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}"/>
  
  <!-- ASCII Art -->
  <g font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="14" fill="{TEXT_COLOR}">
'''
    
    # Add each row without animation
    for i, line in enumerate(ascii_lines):
        y = padding + 14 + i * char_height
        
        # Escape XML special characters
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        svg_content += f'    <text x="{padding}" y="{y}">{escaped_line}</text>\n'
    
    svg_content += '''  </g>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return str(output_path)


def generate_ascii_portrait(
    image_path: str,
    animated_output: str = None,
    static_output: str = None,
    width: int = 80
) -> tuple:
    """
    Generate ASCII portrait SVGs from a processed image.
    
    Args:
        image_path: Path to processed image
        animated_output: Path for animated SVG (optional)
        static_output: Path for static SVG (optional)
        width: ASCII width in characters
    
    Returns:
        Tuple of (animated_path, static_path)
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Default output paths
    if animated_output is None:
        animated_output = image_path.parent.parent / "assets" / "ascii" / "portrait.svg"
    if static_output is None:
        static_output = image_path.parent.parent / "assets" / "ascii" / "portrait-static.svg"
    
    print(f"Converting image to ASCII (width={width})...")
    ascii_lines = image_to_ascii(str(image_path), width)
    
    print(f"Generating animated SVG...")
    animated_path = generate_animated_svg(ascii_lines, animated_output)
    print(f"Saved: {animated_path}")
    
    print(f"Generating static SVG...")
    static_path = generate_static_svg(ascii_lines, static_output)
    print(f"Saved: {static_path}")
    
    return animated_path, static_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_ascii_svg.py <processed-image.png> [animated.svg] [static.svg] [width]")
        print("  processed-image.png: Path to processed image")
        print("  animated.svg: Path for animated output (default: assets/ascii/portrait.svg)")
        print("  static.svg: Path for static output (default: assets/ascii/portrait-static.svg)")
        print("  width: ASCII width in characters (default: 80)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    anim_file = sys.argv[2] if len(sys.argv) > 2 else None
    static_file = sys.argv[3] if len(sys.argv) > 3 else None
    ascii_width = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    
    generate_ascii_portrait(input_file, anim_file, static_file, ascii_width)
    print("\nDone!")