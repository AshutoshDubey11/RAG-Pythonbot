import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(
    page_title="Document AI Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# This CSS pushes the entire application higher up on the screen
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)


# --- BACKEND LOGIC ---
@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )


async def send_rag_query_event(question: str, top_k: int) -> None:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )
    return result[0]


def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


# --- USER INTERFACE ---

# 1. Centered Title with Lavender/Plum text coloring to match the theme
st.markdown("<h1 style='text-align: center; color: #D8B4E2;'>Document AI Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #9A8C98; margin-bottom: 30px;'>Manage your private knowledge base and extract AI insights instantly.</p>",
    unsafe_allow_html=True)

# 2. Main Outer Box framing the entire content
with st.container(border=True):
    # Split into two clear halves with a small spacer in the middle
    col1, col_space, col2 = st.columns([1, 0.05, 1])

    # --- LEFT SIDE: Document Management ---
    with col1:
        st.markdown("<h3 style='color: #C8B6E6;'>Manage Documents</h3>", unsafe_allow_html=True)

        # Inner box to clearly divide the functionality
        with st.container(border=True):
            uploaded = st.file_uploader("Upload secure PDF", type=["pdf"], accept_multiple_files=False)

            if uploaded is not None:
                with st.spinner("Encrypting and indexing..."):
                    path = save_uploaded_pdf(uploaded)
                    asyncio.run(send_rag_ingest_event(path))
                    time.sleep(0.3)
                st.success(f"Successfully indexed: {path.name}")

            st.write("---")

            # Database visualizer
            st.markdown("#### Database Index")
            uploads_dir = Path("uploads")
            if uploads_dir.exists():
                files = list(uploads_dir.glob("*.pdf"))
                if files:
                    for f in reversed(files[-5:]):
                        st.caption(f"• **Indexed:** {f.name}")

                    st.write("")
                    storage_gb = round(len(files) * 0.2, 1)
                    st.progress(min(storage_gb / 10.0, 1.0), text=f"Storage Capacity: {storage_gb} GB / 10 GB")
                else:
                    st.caption("No documents currently indexed.")

    # --- RIGHT SIDE: Knowledge Querying ---
    with col2:
        st.markdown("<h3 style='color: #C8B6E6;'>Query Knowledge Base</h3>", unsafe_allow_html=True)

        # Inner box to clearly divide the functionality
        with st.container(border=True):
            with st.form("rag_query_form", border=False):
                question = st.text_area("Question", placeholder="Ask a question about your documents...", height=175,
                                        label_visibility="collapsed")

                # Advanced settings neatly organized
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    top_k = st.number_input("Retrieve chunks", min_value=1, max_value=20, value=5, step=1)

                st.write("")
                submitted = st.form_submit_button("Generate Analysis", use_container_width=True)

                if submitted and question.strip():
                    with st.spinner("Analyzing vectors..."):
                        event_id = asyncio.run(send_rag_query_event(question.strip(), int(top_k)))
                        output = wait_for_run_output(event_id)
                        answer = output.get("answer", "")
                        sources = output.get("sources", [])

                    st.info(answer or "No answer found in context.")

                    if sources:
                        st.write("")
                        with st.expander("View Referenced Sources"):
                            for s in sources:
                                st.caption(f"- {s}")