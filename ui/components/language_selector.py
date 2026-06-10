import streamlit as st
from config.languages import LANGUAGE_CONFIG


def render_language_badge(lang_code: str):
    c = LANGUAGE_CONFIG.get(lang_code, {})
    st.caption(f"{c.get('flag','🌐')} {c.get('name', lang_code)} — {c.get('native', '')}")


def render_supported_languages():
    st.markdown("**Supported Languages:**")
    for code, info in LANGUAGE_CONFIG.items():
        st.markdown(f"{info['flag']} {info['name']} ({info['native']})")