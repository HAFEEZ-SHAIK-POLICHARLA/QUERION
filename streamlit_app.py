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
st.markdown(
    """
    <style>
    :root {
        --bg-0: #060b14;
        --bg-1: #0b1524;
        --bg-2: #101b2f;
        --glass: rgba(255, 255, 255, 0.08);
        --glass-strong: rgba(255, 255, 255, 0.12);
        --stroke: rgba(255, 255, 255, 0.14);
        --stroke-strong: rgba(255, 255, 255, 0.22);
        --text-main: #eef4ff;
        --text-soft: rgba(238, 244, 255, 0.72);
        --accent: #58efe1;
        --accent-2: #7c9cff;
        --danger: #ff6f91;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }

    html, body, .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(88, 239, 225, 0.12), transparent 26%),
            radial-gradient(circle at 90% 20%, rgba(124, 156, 255, 0.12), transparent 28%),
            radial-gradient(circle at 50% 90%, rgba(88, 239, 225, 0.10), transparent 30%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 45%, var(--bg-2) 100%);
        color: var(--text-main);
    }

    .stApp {
        position: relative;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
        background-size: 52px 52px;
        opacity: 0.35;
        mask-image: radial-gradient(circle at center, black 0%, black 68%, transparent 100%);
        z-index: 0;
        animation: querion-grid 28s linear infinite;
    }

    @keyframes querion-grid {
        from { transform: translate3d(0, 0, 0); }
        to { transform: translate3d(-52px, -52px, 0); }
    }

    .block-container {
        max-width: 1040px;
        padding-top: 1.15rem;
        padding-bottom: 7.5rem;
        position: relative;
        z-index: 1;
    }

    .querion-shell {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .querion-hero {
        padding: 0.85rem 0 0.35rem 0;
    }

    .querion-title {
        margin: 0;
        font-size: clamp(2.3rem, 6vw, 4.15rem);
        line-height: 0.95;
        letter-spacing: -0.04em;
        font-weight: 800;
        color: var(--text-main);
    }

    .querion-title span {
        color: var(--accent);
        text-shadow: 0 0 20px rgba(88, 239, 225, 0.22);
    }

    .querion-subtitle {
        margin: 0.6rem 0 0;
        max-width: 66ch;
        font-size: clamp(0.98rem, 2.3vw, 1.08rem);
        color: var(--text-soft);
        line-height: 1.6;
    }

    .querion-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 0.9rem;
    }

    .querion-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid var(--stroke);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        color: var(--text-soft);
        font-size: 0.92rem;
    }

    .querion-pill strong {
        color: var(--text-main);
        font-weight: 700;
    }

    .querion-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.08));
        border: 1px solid var(--stroke);
        border-radius: 24px;
        box-shadow:
            0 20px 60px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1rem;
    }

    .querion-card h3 {
        margin: 0 0 0.35rem 0;
        font-size: 1.05rem;
        color: var(--text-main);
    }

    .querion-card p, .querion-card small, .querion-card span {
        color: var(--text-soft);
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.07) !important;
        border: 1px dashed rgba(255,255,255,0.22) !important;
        border-radius: 18px !important;
        padding: 0.55rem !important;
    }

    section[data-testid="stFileUploaderDropzone"] div {
        color: var(--text-main) !important;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        background: rgba(255,255,255,0.08) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(255,255,255,0.16) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    section[data-testid="stFileUploaderDropzone"] button svg {
        display: none !important;
    }

    section[data-testid="stFileUploaderDropzone"] svg {
        display: none !important;
    }

    /* Slider */
    div[data-testid="stSlider"] {
        padding-top: 0.15rem;
    }

    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] span,
    div[data-testid="stSlider"] p {
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, rgba(88, 239, 225, 0.18), rgba(124, 156, 255, 0.20)) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 14px !important;
        box-shadow:
            0 10px 30px rgba(0,0,0,0.20),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
    }

    .stButton button:hover {
        border-color: rgba(88, 239, 225, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Chat history */
    div[data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding: 0.45rem 0;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"])
        div[data-testid="stChatMessageContent"] {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"])
        div[data-testid="stChatMessageContent"] {
        background: transparent;
        padding: 0.35rem 0.1rem;
    }

    div[data-testid="stChatMessageContent"] p,
    div[data-testid="stChatMessageContent"] li,
    div[data-testid="stChatMessageContent"] ul,
    div[data-testid="stChatMessageContent"] ol,
    div[data-testid="stChatMessageContent"] span,
    div[data-testid="stChatMessageContent"] strong,
    div[data-testid="stChatMessageContent"] em,
    div[data-testid="stChatMessageContent"] h1,
    div[data-testid="stChatMessageContent"] h2,
    div[data-testid="stChatMessageContent"] h3,
    div[data-testid="stChatMessageContent"] h4,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] strong {
        color: var(--text-main) !important;
        line-height: 1.65;
    }

    /* Chat input glass morphism */
    [data-testid="stBottom"] {
        background: rgba(255,255,255,0.05) !important;
        border-top: 1px solid rgba(255,255,255,0.10) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
    }

    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }

    div[data-testid="stChatInput"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 18px !important;
        box-shadow:
            0 18px 60px rgba(0,0,0,0.28),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(22px) !important;
        -webkit-backdrop-filter: blur(22px) !important;
    }

    div[data-testid="stChatInput"] > div {
        background: transparent !important;
    }

    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--text-main) !important;
        border: none !important;
        caret-color: var(--accent) !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: rgba(238, 244, 255, 0.45) !important;
    }

    button[data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, rgba(88, 239, 225, 0.28), rgba(124, 156, 255, 0.28)) !important;
        border: 1px solid rgba(255,255,255,0.16) !important;
    }

    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* Helper text */
    .querion-help {
        color: var(--text-soft);
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 0.25rem 0 0;
    }

    .querion-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
        margin: 0.6rem 0;
    }

    /* Loading animation */
    .querion-loader-wrap {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 0.15rem 0 0.35rem;
    }

    .querion-loader {
        width: min(100%, 760px);
        padding: 1rem 1rem 1rem 1rem;
        border-radius: 24px;
        background:
            radial-gradient(circle at 20% 20%, rgba(88,239,225,0.13), transparent 28%),
            radial-gradient(circle at 80% 30%, rgba(124,156,255,0.12), transparent 30%),
            rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.16);
        box-shadow:
            0 18px 50px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .querion-orbit {
        position: relative;
        width: 72px;
        height: 72px;
        flex: 0 0 auto;
    }

    .querion-orbit::before,
    .querion-orbit::after {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
    }

    .querion-orbit::before {
        border: 2px solid rgba(255,255,255,0.16);
        box-shadow: inset 0 0 30px rgba(88,239,225,0.12);
        animation: querion-spin 3.2s linear infinite;
    }

    .querion-orbit::after {
        inset: 13px;
        border: 1px solid rgba(88,239,225,0.25);
        animation: querion-pulse-ring 1.8s ease-in-out infinite;
    }

    .querion-dot {
        position: absolute;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: radial-gradient(circle, #ffffff 0%, var(--accent) 40%, rgba(88,239,225,0.15) 100%);
        box-shadow: 0 0 18px rgba(88,239,225,0.55);
        animation: querion-dot-orbit 1.8s linear infinite;
        top: 8px;
        left: 30px;
    }

    .querion-core {
        position: absolute;
        inset: 19px;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 35%, rgba(255,255,255,0.95), rgba(255,255,255,0.45) 24%, rgba(88,239,225,0.18) 65%, rgba(88,239,225,0.08) 100%);
        box-shadow:
            inset 0 0 18px rgba(255,255,255,0.18),
            0 0 24px rgba(124,156,255,0.18);
        animation: querion-core-breathe 1.4s ease-in-out infinite;
    }

    .querion-loader-copy {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        min-width: 0;
    }

    .querion-loader-copy strong {
        font-size: 1.03rem;
        color: var(--text-main);
        letter-spacing: 0.01em;
    }

    .querion-loader-copy span {
        font-size: 0.92rem;
        color: var(--text-soft);
        line-height: 1.5;
    }

    .querion-dots {
        display: inline-flex;
        gap: 0.3rem;
        margin-top: 0.15rem;
    }

    .querion-dots span {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent);
        opacity: 0.9;
        animation: querion-bounce 1s infinite ease-in-out;
    }

    .querion-dots span:nth-child(2) { animation-delay: 0.15s; }
    .querion-dots span:nth-child(3) { animation-delay: 0.3s; }

    @keyframes querion-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes querion-dot-orbit {
        0%   { transform: rotate(0deg) translateX(24px) rotate(0deg); }
        100% { transform: rotate(360deg) translateX(24px) rotate(-360deg); }
    }

    @keyframes querion-core-breathe {
        0%, 100% { transform: scale(0.98); opacity: 0.88; }
        50% { transform: scale(1.04); opacity: 1; }
    }

    @keyframes querion-pulse-ring {
        0%, 100% { opacity: 0.65; transform: scale(0.98); }
        50% { opacity: 1; transform: scale(1.03); }
    }

    @keyframes querion-bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
        40% { transform: translateY(-4px); opacity: 1; }
    }

    /* Mobile */
    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding-top: 0.85rem;
            padding-bottom: 6.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .querion-hero {
            padding-top: 0.2rem;
        }

        .querion-loader {
            padding: 0.9rem 0.9rem 0.85rem;
            gap: 0.8rem;
        }

        .querion-orbit {
            width: 60px;
            height: 60px;
        }

        .querion-core {
            inset: 15px;
        }

        .querion-dot {
            top: 7px;
            left: 24px;
        }

        .stChatInput textarea {
            font-size: 16px !important; /* prevents iOS zoom */
        }

        .querion-title {
            font-size: clamp(2rem, 10vw, 3.2rem);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
