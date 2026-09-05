import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import uuid
import streamlit as st
import requests

from ui.components.upload_panel import render_upload_panel
from ui.components.chat_window import render_chat_history
from ui.components.language_selector import render_supported_languages
from config.settings import API_URL

st.set_page_config(page_title="BharatBot 🇮🇳", page_icon="🇮🇳", layout="wide")
st.title("🇮🇳 BharatBot")
st.caption("Upload any document. Chat in any Indian language.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "files" not in st.session_state:
    st.session_state.files = []

with st.sidebar:
    render_upload_panel()
    st.divider()
    render_supported_languages()

render_chat_history(st.session_state.messages)

query = st.chat_input("Type in any language...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{API_URL}/chat",
                json={"query": query, "session_id": st.session_state.session_id}
            )
            if res.status_code == 200:
                data = res.json()
                st.write(data["response"])
                st.caption(f"📄 {', '.join(data['sources'])}")
                st.caption(f"Detected: {data['detected_language']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["response"],
                    "sources": data["sources"],
                    "lang": data["detected_language"]
                })
            else:
                st.error("API error. Run: uvicorn api.main:app --reload")