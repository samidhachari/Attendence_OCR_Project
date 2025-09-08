
# import os
# from typing import Tuple
# from PIL import Image, ImageOps, ImageFilter
# import pytesseract

# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"


# ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff"}

# def is_image(filename: str) -> bool:
#     _, ext = os.path.splitext(filename.lower())
#     return ext in ALLOWED_EXT

# def _preprocess(img: Image.Image) -> Image.Image:
#     # convert to grayscale, slight sharpening and increase contrast via inversion trick
#     img = img.convert("L")
#     img = img.filter(ImageFilter.SHARPEN)
#     # auto-contrast (helps OCR on some inputs)
#     img = ImageOps.autocontrast(img)
#     return img

# def extract_text_from_image(image_path: str) -> Tuple[str, dict]:
#     """
#     Basic OCR wrapper using pytesseract. Returns raw text and a placeholder dict
#     (we may add bbox/tsv in future).
#     """
#     img = Image.open(image_path)
#     img = _preprocess(img)
#     text = pytesseract.image_to_string(img)
#     # we might later return detailed tsv data; for now keep simple
#     return text, {}


import os
from typing import Tuple
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
import cv2
import numpy as np

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}

def is_image(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

def _preprocess(img_path: str) -> Image.Image:
    """Enhanced preprocessing for various image types"""
    
    # Read image with OpenCV
    cv_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if cv_img is None:
        raise ValueError(f"Could not read image: {img_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Resize for better OCR (but not too much to avoid blur)
    scale_percent = 150  # Moderate scaling
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
    
    # Noise reduction
    gray = cv2.medianBlur(gray, 3)
    
    # Contrast enhancement
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    
    # Adaptive thresholding for better binarization
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up text
    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Convert back to PIL
    pil_img = Image.fromarray(thresh)
    
    # Additional PIL enhancements
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(2.0)
    
    return pil_img

def extract_text_from_image(image_path: str) -> Tuple[str, dict]:
    """Run OCR with multiple configurations for better results"""
    
    processed = _preprocess(image_path)
    
    # Try different configurations
    configs = [
        r'--oem 3 --psm 6',  # Uniform block of text
        r'--oem 3 --psm 4',  # Single column of text
        r'--oem 3 --psm 3'   # Fully automatic
    ]
    
    best_text = ""
    best_conf = 0
    
    for config in configs:
        try:
            # Get both text and confidence data
            data = pytesseract.image_to_data(processed, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            
            if avg_conf > best_conf:
                best_conf = avg_conf
                best_text = pytesseract.image_to_string(processed, config=config)
        except Exception:
            continue
    
    # Fallback to basic config if none worked well
    if not best_text:
        best_text = pytesseract.image_to_string(processed, config=r'--oem 3 --psm 6')
    
    return best_text, {"confidence": best_conf}