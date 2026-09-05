import fitz
import pytesseract
from PIL import Image
from config.languages import TESSERACT_ALL, LANGUAGE_CONFIG


def _page_image(page):
    pix = page.get_pixmap(dpi=300)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def _detect_ocr_language(doc) -> str:
    # OCR just the first page with the full multi-language set to sample enough
    # text for language detection. Loading all 10 language models for the WHOLE
    # document causes Tesseract to misread characters as similar-looking glyphs
    # from unrelated scripts (e.g. English text corrupted with stray Kannada/
    # Malayalam characters) - so the real OCR pass below uses only the detected
    # language instead.
    from tools.language_detector import detect_language

    sample_text = pytesseract.image_to_string(_page_image(doc[0]), lang=TESSERACT_ALL)
    detected = detect_language(sample_text[:1000])
    tess_code = LANGUAGE_CONFIG.get(detected["code"], {}).get("tesseract", "eng")
    return tess_code if tess_code == "eng" else f"{tess_code}+eng"


def load_scanned_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    ocr_lang = _detect_ocr_language(doc)
    print(f"  Detected OCR language: {ocr_lang}")

    full_text = ""
    for i, page in enumerate(doc):
        print(f"  OCR page {i+1}/{len(doc)}...")
        full_text += pytesseract.image_to_string(_page_image(page), lang=ocr_lang) + "\n"
    doc.close()
    return full_text
