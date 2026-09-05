import re
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, SEMANTIC_BREAKPOINT_PERCENTILE

MIN_CHUNK_LENGTH = 20

# । = Devanagari danda (Hindi/Marathi sentence end), ۔ = Urdu full stop
_SEPARATORS = ["\n\n", "\n", "।", "۔", ".", " ", ""]
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.।۔!?])\s+")


def _split_sentences(text: str) -> list:
    sentences = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        sentences.extend(s.strip() for s in _SENTENCE_SPLIT_RE.split(para) if s.strip())
    return sentences


def _cosine_similarity(a, b) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


def _group_by_similarity(sentences: list, embeddings) -> list:
    # A fixed similarity threshold doesn't transfer across embedding models -
    # e.g. text-embedding-3-small's consecutive-sentence similarity often
    # sits below 0.5 even within one topic. Instead, treat only the most
    # dissimilar transitions *within this document* as topic breaks: compute
    # every consecutive-sentence distance, then split at the ones in the top
    # (100 - percentile)% - self-calibrating regardless of the embedding
    # model's absolute similarity scale.
    distances = [
        1 - _cosine_similarity(embeddings[i - 1], embeddings[i])
        for i in range(1, len(embeddings))
    ]
    if not distances:
        return [sentences[0]]

    breakpoint_distance = float(np.percentile(distances, SEMANTIC_BREAKPOINT_PERCENTILE))

    groups = [[sentences[0]]]
    for i, distance in enumerate(distances, start=1):
        if distance >= breakpoint_distance:
            groups.append([sentences[i]])
        else:
            groups[-1].append(sentences[i])
    return [" ".join(g) for g in groups]


def _recursive_split(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=_SEPARATORS
    )
    return splitter.split_text(text)


def chunk_text(text: str, source_file: str) -> list:
    sentences = _split_sentences(text)

    if len(sentences) <= 1:
        raw_chunks = _recursive_split(text)
    else:
        # Group sentences by embedding similarity so each chunk stays on one
        # topic, then fall back to recursive character splitting for any
        # resulting group still too large for CHUNK_SIZE.
        from ingestion.embedder import embed_chunks
        sentence_embeddings = embed_chunks([{"text": s} for s in sentences])
        semantic_chunks = _group_by_similarity(sentences, sentence_embeddings)

        raw_chunks = []
        for chunk in semantic_chunks:
            if len(chunk) > CHUNK_SIZE:
                raw_chunks.extend(_recursive_split(chunk))
            else:
                raw_chunks.append(chunk)

    raw_chunks = [c.strip() for c in raw_chunks if c.strip()]

    # Merge any fragment too short to be useful on its own into the previous
    # chunk instead of silently dropping it (e.g. a short trailing sentence).
    merged = []
    for c in raw_chunks:
        if merged and len(c) < MIN_CHUNK_LENGTH:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)

    return [
        {"text": c, "source": source_file, "chunk_id": i}
        for i, c in enumerate(merged)
    ]
