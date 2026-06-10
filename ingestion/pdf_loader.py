import fitz


def load_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = "".join([page.get_text() for page in doc])
    doc.close()

    if len(text.strip()) < 100:
        from ingestion.ocr_loader import load_scanned_pdf
        print(f"Thin text layer detected. Switching to OCR for: {file_path}")
        text = load_scanned_pdf(file_path)

    return text