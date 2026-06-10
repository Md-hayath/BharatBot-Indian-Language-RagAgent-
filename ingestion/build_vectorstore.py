import os
import faiss
import pickle
import numpy as np
from config.settings import (
    DATA_RAW_PATH, VECTOR_STORE_PATH,
    INDEX_FILE, META_FILE
)
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_chunks


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


def ingest_file(file_path: str) -> int:
    print(f"\nIngesting: {file_path}")
    text = load_document(file_path)
    chunks = chunk_text(text, os.path.basename(file_path))
    if not chunks:
        print("No chunks extracted.")
        return 0

    embeddings = embed_chunks(chunks).astype("float32")
    dim = embeddings.shape[1]

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []

    index.add(embeddings)
    metadata.extend(chunks)

    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Added {len(chunks)} chunks.")
    return len(chunks)


def build_from_raw_folder():
    supported = [".pdf", ".docx", ".txt"]
    total = 0
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