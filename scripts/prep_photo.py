#!/usr/bin/env python3
"""
Prepare source photo for ASCII portrait generation.
Handles background removal, grayscale conversion, contrast enhancement, and resizing.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install pillow numpy")
    sys.exit(1)

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    print("WARNING: rembg not installed. Background removal disabled.")
    print("Install with: pip install rembg")


def prepare_photo(
    input_path: str,
    output_path: str = None,
    width: int = 80,
    remove_bg: bool = True,
    enhance_contrast: bool = True
) -> str:
    """
    Prepare a photo for ASCII art conversion.
    
    Args:
        input_path: Path to source photo
        output_path: Path to save processed image (optional)
        width: Target width in characters (for aspect ratio calculation)
        remove_bg: Whether to remove background
        enhance_contrast: Whether to enhance contrast
    
    Returns:
        Path to processed image
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Source photo not found: {input_path}")
    
    if output_path is None:
        output_path = input_path.parent / "processed-photo.png"
    else:
        output_path = Path(output_path)
    
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    
    # Convert to RGBA for processing
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    # Remove background if requested and rembg is available
    if remove_bg and HAS_REMBG:
        print("Removing background...")
        img = remove(img)
    
    # Convert to grayscale
    print("Converting to grayscale...")
    img_gray = img.convert("L")
    
    # Enhance contrast
    if enhance_contrast:
        print("Enhancing contrast...")
        enhancer = ImageEnhance.Contrast(img_gray)
        img_gray = enhancer.enhance(1.5)
        
        # Apply slight sharpening
        img_gray = img_gray.filter(ImageFilter.SHARPEN)
    
    # Calculate target dimensions maintaining aspect ratio
    # Terminal characters are typically taller than wide (aspect ratio ~0.5)
    char_aspect = 0.5
    original_width, original_height = img_gray.size
    original_aspect = original_height / original_width
    
    target_width = width
    target_height = int(width * original_aspect * char_aspect)
    
    # Resize image
    print(f"Resizing to {target_width}x{target_height}...")
    img_resized = img_gray.resize(
        (target_width, target_height),
        Image.Resampling.LANCZOS
    )
    
    # Save processed image
    img_resized.save(output_path)
    print(f"Saved processed image: {output_path}")
    
    return str(output_path)


def get_pixel_data(image_path: str) -> list:
    """
    Get pixel brightness data from an image.
    
    Args:
        image_path: Path to processed image
    
    Returns:
        2D list of pixel values (0-255)
    """
    img = Image.open(image_path).convert("L")
    width, height = img.size
    
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(img.getpixel((x, y)))
        pixels.append(row)
    
    return pixels


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo.jpg> [output.png] [width]")
        print("  source-photo.jpg: Path to source photo")
        print("  output.png: Path to save processed image (default: processed-photo.png)")
        print("  width: Target width in characters (default: 80)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    target_width = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    
    result = prepare_photo(input_file, output_file, target_width)
    print(f"\nDone! Processed image saved to: {result}")