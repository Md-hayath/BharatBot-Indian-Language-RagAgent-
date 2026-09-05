from config.settings import (
    SARVAM_API_KEY, ANTHROPIC_API_KEY,
    SARVAM_MODEL, CLAUDE_MODEL,
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    TOP_K_RESULTS
)
from tools.language_detector import detect_language
from ingestion.embedder import embed_query
from ingestion.vector_store import search, has_documents
from agents.state import BharatBotState
from config.languages import LANGUAGE_CONFIG

from openai import OpenAI
from sarvamai import SarvamAI
from anthropic import Anthropic

# Azure's unified v1 API endpoint (".../openai/v1") works directly with the
# standard OpenAI client via base_url - no api_version needed.
azure_client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT,
)
sarvam = SarvamAI(api_subscription_key=SARVAM_API_KEY)
claude = Anthropic(api_key=ANTHROPIC_API_KEY)

# Sarvam-30B is trained specifically on Indian languages, so it's the
# primary model for them; Azure GPT-4o is primary for everything else.
INDIC_LANGUAGES = set(LANGUAGE_CONFIG.keys()) - {"en"}


def detect_language_node(state: BharatBotState) -> BharatBotState:
    result = detect_language(state["query"])
    state["query_language"] = result["code"]
    return state


def retrieve_docs_node(state: BharatBotState) -> BharatBotState:
    if not has_documents():
        state["retrieved_docs"] = []
        state["sources"] = []
        return state

    q_vec = embed_query(state["query"])
    results = search(q_vec, TOP_K_RESULTS)

    state["retrieved_docs"] = [text for text, source in results]
    state["sources"] = list({source for text, source in results})
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
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    def call_azure():
        resp = azure_client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=messages
        )
        return resp.choices[0].message.content

    def call_sarvam():
        resp = sarvam.chat.completions(model=SARVAM_MODEL, messages=messages)
        return resp.choices[0].message.content

    def call_claude():
        resp = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return resp.content[0].text

    primary, secondary = (call_sarvam, call_azure) if lang in INDIC_LANGUAGES else (call_azure, call_sarvam)

    try:
        state["response"] = primary()
    except Exception:
        try:
            state["response"] = secondary()
        except Exception:
            state["response"] = call_claude()

    return state