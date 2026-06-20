from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://querion-backend-1.onrender.com").rstrip("/")

st.set_page_config(
    page_title="Querion",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Theme


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=45)
def backend_health() -> tuple[bool, str]:
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.ok:
            return True, "Online"
        return False, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def response_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return (
                payload.get("error")
                or payload.get("detail")
                or json.dumps(payload, ensure_ascii=False)
            )
        return str(payload)
    except Exception:
        text = (response.text or "").strip()
        return text if text else f"HTTP {response.status_code}"


def upload_pdf_to_backend(uploaded_file) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }
    response = requests.post(
        f"{BACKEND_URL}/upload",
        files=files,
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(response_error_message(response))
    return response.json()


def query_backend(question: str, top_k: int) -> dict[str, Any]:
    response = requests.post(
        f"{BACKEND_URL}/query",
        json={"question": question, "top_k": int(top_k)},
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(response_error_message(response))
    return response.json()


def render_loader() -> None:
    st.markdown(
        """
        <div class="querion-loader-wrap">
            <div class="querion-loader">
                <div class="querion-orbit">
                    <div class="querion-dot"></div>
                    <div class="querion-core"></div>
                </div>
                <div class="querion-loader-copy">
                    <strong>Querion is scanning your document</strong>
                    <span>
                        Matching the most relevant passages and shaping an answer
                        <span class="querion-dots"><span></span><span></span><span></span></span>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: list[str]) -> None:
    if not sources:
        return

    with st.expander("Sources"):
        for source in sources:
            st.write(f"• {source}")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

health_ok, health_status = backend_health()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="querion-shell">
        <section class="querion-hero">
            <h1 class="querion-title">Querion<span>.</span></h1>
            <p class="querion-subtitle">
                Upload a PDF, ask a question, and get answers grounded in your own documents.
                The interface is built for mobile and desktop, with a glassmorphism chat bar and
                a custom scanning animation while Querion searches.
            </p>
            <div class="querion-status-row">
                <div class="querion-pill">
                    <strong>Backend</strong>
                    <span>{status}</span>
                </div>
                <div class="querion-pill">
                    <strong>Mode</strong>
                    <span>PDF RAG</span>
                </div>
            </div>
        </section>
    </div>
    """.format(status="Online" if health_ok else f"Offline · {health_status}"),
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Upload / Settings
# ---------------------------------------------------------------------------
st.markdown('<div class="querion-divider"></div>', unsafe_allow_html=True)
st.markdown("### 📄 Knowledge Base")
st.markdown(
    '<p class="querion-help">Upload a PDF here. The control stays visible on mobile and desktop.</p>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)

if uploaded_file is not None:
    st.caption(f"Selected file: {uploaded_file.name}")

search_depth = st.slider(
    "How thoroughly should Querion search?",
    min_value=3,
    max_value=12,
    value=5,
    step=1,
    help="Higher values search more parts of the document before answering.",
)

col_upload, col_clear = st.columns([2, 1], gap="small")

with col_upload:
    ingest_clicked = st.button("Ingest PDF", use_container_width=True, type="primary")

with col_clear:
    clear_clicked = st.button("🗑️ Clear chat", use_container_width=True)

if clear_clicked:
    st.session_state.messages = []
    st.rerun()

if ingest_clicked:
    if uploaded_file is None:
        st.warning("Please choose a PDF first.")
    else:
        try:
            with st.spinner("Uploading and indexing your PDF..."):
                result = upload_pdf_to_backend(uploaded_file)

            st.session_state.last_uploaded_name = result.get("source", uploaded_file.name)
            st.success(
                f"Ingested {result.get('source', uploaded_file.name)} "
                f"({result.get('chunks', 0)} chunks indexed)"
            )
            st.toast("PDF indexed successfully")
        except Exception as exc:
            st.error(f"Upload failed: {exc}")

st.markdown('<div class="querion-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        """
        <div class="querion-card">
            <h3>Start the conversation</h3>
            <p class="querion-help">
                Upload a document first, then ask something like:
                “What is this document about?” or “Summarize the key points.”
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            render_sources(message["sources"])

# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------
question = st.chat_input("Ask Querion about the uploaded document…")

if question and question.strip():
    question = question.strip()

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    loader_placeholder = st.empty()
    loader_placeholder.markdown(
        """
        <div class="querion-loader-wrap">
            <div class="querion-loader">
                <div class="querion-orbit">
                    <div class="querion-dot"></div>
                    <div class="querion-core"></div>
                </div>
                <div class="querion-loader-copy">
                    <strong>Querion is scanning your document</strong>
                    <span>
                        Matching the most relevant passages and shaping an answer
                        <span class="querion-dots"><span></span><span></span><span></span></span>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = query_backend(question, int(search_depth))
        answer = (result.get("answer") or "").strip()
        sources = result.get("sources", [])

        loader_placeholder.empty()

        with st.chat_message("assistant"):
            st.write(answer or "(No answer)")
            render_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer or "(No answer)",
                "sources": sources,
            }
        )

    except Exception as exc:
        loader_placeholder.empty()
        error_message = f"Query failed: {exc}"
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
                "sources": [],
            }
        )
