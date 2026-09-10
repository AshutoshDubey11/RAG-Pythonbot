from pathlib import Path
import time
import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

st.set_page_config(page_title="Document AI Assistant", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #D8B4E2;'>Document AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9A8C98; margin-bottom: 30px;'>Manage your private knowledge base and extract AI insights instantly.</p>", unsafe_allow_html=True)

with st.container(border=True):
    col1, col_space, col2 = st.columns([1, 0.05, 1])

    with col1:
        st.markdown("<h3 style='color: #C8B6E6;'>Manage Documents</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            uploaded = st.file_uploader("Upload secure PDF", type=["pdf"], accept_multiple_files=False)
            if uploaded:
                with st.spinner("Reading the document..."):
                    backend_url = os.getenv("BACKEND_URL", "https://docuchat-backend-rlyw.onrender.com")
                    resp = requests.post(f"{backend_url}/api/upload", files={"file": (uploaded.name, uploaded.getvalue())})
                    time.sleep(0.3)
                if resp.status_code == 200:
                    st.success(f"Successfully indexed: {uploaded.name}")
                    if uploaded.name not in st.session_state.indexed_files:
                        st.session_state.indexed_files.append(uploaded.name)
                else:
                    st.error(f"Failed to index: {resp.text}")

            st.write("---")
            st.markdown("#### Session Index")
            if st.session_state.indexed_files:
                for fname in reversed(st.session_state.indexed_files[-5:]):
                    st.caption(f"• **Indexed:** {fname}")
                st.write("")
                storage_gb = round(len(st.session_state.indexed_files) * 0.2, 1)
                st.progress(min(storage_gb / 10.0, 1.0), text=f"Session Capacity: {storage_gb} GB / 10 GB")
            else:
                st.caption("No documents currently  uploaded in this session.")

    with col2:
        st.markdown("<h3 style='color: #C8B6E6;'>Query Knowledge Base</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("rag_query_form", border=False):
                question = st.text_input("Question", placeholder="Ask a question about your documents...", label_visibility="collapsed")
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    top_k = st.number_input("Retrieve chunks", min_value=1, max_value=20, value=5, step=1)

                st.write("")
                submitted = st.form_submit_button("Answer", use_container_width=True)

                if submitted and question.strip():
                    with st.spinner("Finding Answer..."):
                        backend_url = os.getenv("BACKEND_URL", "https://docuchat-backend-rlyw.onrender.com")
                        resp = requests.post(f"{backend_url}/api/query", json={"question": question.strip(), "top_k": int(top_k)})
                        if resp.status_code == 200:
                            output = resp.json()
                            answer = output.get("answer", "")
                            sources = output.get("sources", [])
                        else:
                            answer = f"Error: {resp.text}"
                            sources = []

                    st.info(answer or "No answer found.")
                    if sources:
                        st.write("")
                        with st.expander("View Referenced Sources"):
                            for s in sources:
                                st.caption(f"- {s}")