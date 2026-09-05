import fitz
import pytesseract
from PIL import Image
from config.languages import TESSERACT_ALL


def load_scanned_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    full_text = ""
    for i, page in enumerate(doc):
        print(f"  OCR page {i+1}/{len(doc)}...")
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        full_text += pytesseract.image_to_string(img, lang=TESSERACT_ALL) + "\n"
    doc.close()
    return full_text