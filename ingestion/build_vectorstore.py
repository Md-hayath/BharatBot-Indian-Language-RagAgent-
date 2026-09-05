import os
from config.settings import DATA_RAW_PATH
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_chunks
from ingestion.vector_store import add_chunks


def load_document(file_path: str) -> str:
    ext = file_path.split(".")[-1].lower()
    if ext == "pdf":
        return load_pdf(file_path)
    elif ext == "docx":
        from docx import Document
        return "\n".join([p.text for p in Document(file_path).paragraphs])
    elif ext == "txt":
        return open(file_path, encoding="utf-8").read()
    else:
        raise ValueError(f"Unsupported: {ext}")


def ingest_file(file_path: str, text: str = None) -> int:
    print(f"\nIngesting: {file_path}")
    if text is None:
        text = load_document(file_path)
    chunks = chunk_text(text, os.path.basename(file_path))
    if not chunks:
        print("No chunks extracted.")
        return 0

    embeddings = embed_chunks(chunks)
    add_chunks(chunks, embeddings)

    print(f"Added {len(chunks)} chunks.")
    return len(chunks)


def build_from_raw_folder():
    supported = [".pdf", ".docx", ".txt"]
    total = 0
    os.makedirs(DATA_RAW_PATH, exist_ok=True)
    for lang_folder in os.listdir(DATA_RAW_PATH):
        folder_path = os.path.join(DATA_RAW_PATH, lang_folder)
        if not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if os.path.splitext(filename)[1].lower() in supported:
                file_path = os.path.join(folder_path, filename)
                total += ingest_file(file_path)
    print(f"\nTotal chunks indexed: {total}")


if __name__ == "__main__":
    build_from_raw_folder()