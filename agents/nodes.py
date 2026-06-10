import os
import faiss
import pickle
import numpy as np

from config.settings import (
    SARVAM_API_KEY, ANTHROPIC_API_KEY,
    SARVAM_MODEL, CLAUDE_MODEL,
    INDEX_FILE, META_FILE, TOP_K_RESULTS
)
from tools.language_detector import detect_language
from ingestion.embedder import embed_query
from agents.state import BharatBotState

from sarvamai import SarvamAI
from anthropic import Anthropic

sarvam = SarvamAI(api_subscription_key=SARVAM_API_KEY)
claude = Anthropic(api_key=ANTHROPIC_API_KEY)


def detect_language_node(state: BharatBotState) -> BharatBotState:
    result = detect_language(state["query"])
    state["query_language"] = result["code"]
    return state


def retrieve_docs_node(state: BharatBotState) -> BharatBotState:
    if not os.path.exists(INDEX_FILE):
        state["retrieved_docs"] = []
        state["sources"] = []
        return state

    q_vec = embed_query(state["query"]).astype("float32").reshape(1, -1)
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        metadata = pickle.load(f)

    _, indices = index.search(q_vec, TOP_K_RESULTS)
    docs, sources = [], []
    for idx in indices[0]:
        if 0 <= idx < len(metadata):
            docs.append(metadata[idx]["text"])
            sources.append(metadata[idx]["source"])

    state["retrieved_docs"] = docs
    state["sources"] = list(set(sources))
    return state


def generate_response_node(state: BharatBotState) -> BharatBotState:
    query = state["query"]
    docs = state["retrieved_docs"]
    lang = state["query_language"]

    if not docs:
        state["response"] = "Please upload a document first so I can answer your questions."
        return state

    context = "\n\n---\n\n".join(docs)
    system_prompt = f"""You are BharatBot, a multilingual document assistant.
Answer only from the provided context.
User language code: {lang}
Always respond in the exact same language the user wrote in.
Cite the source document at the end."""

    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        resp = sarvam.chat.completions(
            model=SARVAM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        state["response"] = resp.choices[0].message.content
    except Exception:
        resp = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        state["response"] = resp.content[0].text

    return state