"""
prep_photo.py

A flatly-lit face converts to a dark, unreadable ASCII blob. Three steps fix
that before we ever touch character glyphs:

  1. Remove the background with rembg so only the subject remains.
  2. Boost local contrast with OpenCV's CLAHE (contrast-limited adaptive
     histogram equalization) -- this is what gives a flat face real
     highlights and shadows.
  3. Composite onto pure white so the background maps to the blank end of
     the ASCII ramp (white -> spaces) in make_ascii_svg.py.

Output is a grayscale source-prepped.png sitting next to the input photo.
Run this once per photo -- not part of the daily automation.

Usage:
    python prep_photo.py source-photo.jpg
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    out_path = src_path.parent / "source-prepped.png"

    # 1. Remove background -> RGBA with transparent background.
    raw = Image.open(src_path).convert("RGBA")
    cutout = remove(raw)

    # 2. Composite onto pure white so background -> white -> blank glyph.
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")

    # 3. CLAHE local contrast boost on the grayscale subject.
    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    Image.fromarray(boosted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
