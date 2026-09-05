from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, source_file: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "\u0964", ".", " ", ""]
    )
    chunks = splitter.split_text(text)
    return [
        {"text": c, "source": source_file, "chunk_id": i}
        for i, c in enumerate(chunks)
        if len(c.strip()) > 20
    ]
