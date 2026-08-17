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
    raw = Image.open(src_path).convert("RGBA")
    cutout = remove(raw)
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")
    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)
    Image.fromarray(boosted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
