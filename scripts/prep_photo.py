#!/usr/bin/env python3
"""
Prepare source photo for ASCII portrait generation.
Supports JPG/JPEG/PNG input and uses Pillow only by default.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("ERROR: Pillow is not installed. Run: pip install pillow")
    sys.exit(1)

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    print("WARNING: rembg not installed. Background removal disabled.")


def prepare_photo(
    input_path: str,
    output_path: str = None,
    width: int = 80,
    remove_bg: bool = True,
    enhance_contrast: bool = True
) -> str:
    """Prepare a photo for ASCII art conversion."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Source photo not found: {input_path}")

    output_path = Path(output_path) if output_path else input_path.parent / "processed-photo.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading image: {input_path}")
    img = Image.open(input_path).convert("RGBA")

    if remove_bg and HAS_REMBG:
        print("Removing background...")
        img = remove(img)

    img_gray = img.convert("L")

    if enhance_contrast:
        print("Enhancing contrast...")
        img_gray = ImageEnhance.Contrast(img_gray).enhance(1.5)
        img_gray = img_gray.filter(ImageFilter.SHARPEN)

    # Terminal characters are taller than they are wide, so compensate for that ratio.
    original_width, original_height = img_gray.size
    target_height = max(1, int(width * (original_height / original_width) * 0.5))
    print(f"Resizing to {width}x{target_height}...")
    img_resized = img_gray.resize((width, target_height), Image.Resampling.LANCZOS)
    img_resized.save(output_path)
    print(f"Saved processed image: {output_path}")
    return str(output_path)


def get_pixel_data(image_path: str) -> list:
    """Get pixel brightness data from an image."""
    img = Image.open(image_path).convert("L")
    width, height = img.size
    return [[img.getpixel((x, y)) for x in range(width)] for y in range(height)]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo.png|jpg> [output.png] [width]")
        print("  source photo: JPG, JPEG, or PNG")
        print("  output.png: processed image path (default: processed-photo.png)")
        print("  width: target ASCII width (default: 80)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    target_width = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    result = prepare_photo(input_file, output_file, target_width)
    print(f"\nDone! Processed image saved to: {result}")
