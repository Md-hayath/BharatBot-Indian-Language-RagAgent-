import streamlit as st
from ui.components.language_selector import render_language_badge


def render_chat_history(messages: list):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("sources"):
                    st.caption(f"📄 Sources: {', '.join(msg['sources'])}")
                if msg.get("lang"):
                    render_language_badge(msg["lang"])