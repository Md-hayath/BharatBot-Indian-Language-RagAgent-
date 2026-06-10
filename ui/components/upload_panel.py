import streamlit as st
import requests

API_URL = "http://localhost:8000"


def render_upload_panel():
    st.header("📁 Upload Documents")
    file = st.file_uploader(
        "Any language — PDF, DOCX, TXT",
        type=["pdf", "docx", "txt"]
    )
    if file:
        with st.spinner(f"Processing {file.name}..."):
            res = requests.post(
                f"{API_URL}/upload",
                files={"file": (file.name, file.getvalue(), file.type)}
            )
            if res.status_code == 200:
                data = res.json()
                st.success(f"✅ {data['filename']} — {data['chunks_added']} chunks")
                if "files" not in st.session_state:
                    st.session_state.files = []
                st.session_state.files.append(data["filename"])
            else:
                st.error("Upload failed. Is the API running on port 8000?")

    if st.session_state.get("files"):
        st.markdown("**Indexed documents:**")
        for f in st.session_state.files:
            st.markdown(f"- 📄 {f}")