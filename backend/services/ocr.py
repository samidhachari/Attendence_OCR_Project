import os
from typing import Tuple
from PIL import Image, ImageOps, ImageFilter
import pytesseract

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff"}

def is_image(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

def _preprocess(img: Image.Image) -> Image.Image:
    # convert to grayscale, slight sharpening and increase contrast via inversion trick
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    # auto-contrast (helps OCR on some inputs)
    img = ImageOps.autocontrast(img)
    return img

def extract_text_from_image(image_path: str) -> Tuple[str, dict]:
    """
    Basic OCR wrapper using pytesseract. Returns raw text and a placeholder dict
    (we may add bbox/tsv in future).
    """
    img = Image.open(image_path)
    img = _preprocess(img)
    text = pytesseract.image_to_string(img)
    # we might later return detailed tsv data; for now keep simple
    return text, {}











