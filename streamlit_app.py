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
        --bg-0: #071018;
        --bg-1: #08151f;
        --bg-2: #0b1d28;
        --surface: #ffffff;
        --surface-2: #f6fffe;
        --stroke: rgba(17, 24, 39, 0.10);
        --stroke-strong: rgba(34, 211, 238, 0.22);
        --text-main: #10222d;
        --text-soft: #5f7680;
        --accent: #22d3ee;
        --accent-2: #10b981;
        --accent-3: #67e8f9;
        --danger: #ef4444;
        --shadow: 0 18px 50px rgba(16, 185, 129, 0.08), 0 10px 32px rgba(34, 211, 238, 0.06);
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background:
            radial-gradient(circle at 12% 12%, rgba(34,211,238,0.12), transparent 28%),
            radial-gradient(circle at 88% 18%, rgba(16,185,129,0.10), transparent 26%),
            radial-gradient(circle at 52% 88%, rgba(103,232,249,0.10), transparent 30%),
            linear-gradient(180deg, #f8fffe 0%, #f1fffd 52%, #e7fffb 100%) !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    .main .block-container {
        background: transparent !important;
    }

    .stApp {
        position: relative;
    }

    



    @keyframes querion-grid {
        from { transform: translate3d(0, 0, 0); }
        to { transform: translate3d(-56px, -56px, 0); }
    }

    @keyframes querion-glow {
        0%, 100% { opacity: 0.75; }
        50% { opacity: 1; }
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
        font-size: clamp(2.25rem, 6vw, 4.25rem);
        line-height: 0.95;
        letter-spacing: -0.04em;
        font-weight: 900;
        color: var(--text-main);
    }

    .querion-title span {
        color: var(--accent);
        text-shadow: 0 0 18px rgba(34, 211, 238, 0.18);
    }

    .querion-subtitle {
        margin: 0.65rem 0 0;
        max-width: 72ch;
        font-size: clamp(0.98rem, 2.2vw, 1.08rem);
        color: var(--text-soft);
        line-height: 1.65;
    }

    .querion-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 0.95rem;
    }

    .querion-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.82rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(16, 185, 129, 0.16);
        color: var(--text-soft);
        font-size: 0.92rem;
        box-shadow: 0 8px 28px rgba(16, 185, 129, 0.06);
    }

    .querion-pill strong {
        color: var(--text-main);
        font-weight: 800;
    }

    .querion-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(246,255,254,0.95));
        border: 1px solid rgba(16, 185, 129, 0.12);
        border-radius: 24px;
        box-shadow: var(--shadow);
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

    .querion-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(34,211,238,0.35), rgba(16,185,129,0.38), transparent);
        margin: 0.7rem 0;
    }

    .querion-help {
        color: var(--text-soft);
        font-size: 0.95rem;
        line-height: 1.55;
        margin: 0.25rem 0 0;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(246,255,254,0.96)) !important;
        border: 1px solid rgba(34, 211, 238, 0.22) !important;
        border-radius: 18px !important;
        padding: 0.6rem !important;
        box-shadow: var(--shadow);
    }

    section[data-testid="stFileUploaderDropzone"] * {
        color: var(--text-main) !important;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(16, 185, 129, 0.12)) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(34, 211, 238, 0.18) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        font-weight: 700 !important;
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
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.14), rgba(16, 185, 129, 0.16)) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(16, 185, 129, 0.18) !important;
        border-radius: 14px !important;
        box-shadow: var(--shadow) !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em;
    }

    .stButton button:hover {
        border-color: rgba(34, 211, 238, 0.45) !important;
        transform: translateY(-1px);
    }

    /* Chat history */
    div[data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding: 0.45rem 0;
    }

    div[data-testid="stChatMessageContent"] {
        background: rgba(255,255,255,0.96) !important;
        border: 1px solid rgba(16, 185, 129, 0.12) !important;
        border-radius: 18px !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.05) !important;
        padding: 0.85rem 0.95rem !important;
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

    /* Chat input */
   
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }

    div[data-testid="stChatInput"] {
        background: rgba(255,255,255,0.98) !important;
        border: 1px solid rgba(16, 185, 129, 0.14) !important;
        border-radius: 18px !important;
        box-shadow: 0 16px 44px rgba(16,185,129,0.05) !important;
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
        color: rgba(95, 118, 128, 0.72) !important;
    }

    button[data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(16, 185, 129, 0.22)) !important;
        border: 1px solid rgba(16, 185, 129, 0.18) !important;
    }

    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #0f1720 !important;
        color: #0f1720 !important;
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
        padding: 0.95rem 1rem;
        border-radius: 24px;
        background:
            radial-gradient(circle at 20% 20%, rgba(34,211,238,0.14), transparent 28%),
            radial-gradient(circle at 82% 30%, rgba(16,185,129,0.12), transparent 30%),
            rgba(255,255,255,0.97);
        border: 1px solid rgba(34,211,238,0.18);
        box-shadow: var(--shadow);
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
        border: 2px solid rgba(16,185,129,0.18);
        box-shadow: inset 0 0 24px rgba(34,211,238,0.10);
        animation: querion-spin 3.2s linear infinite;
    }

    .querion-orbit::after {
        inset: 13px;
        border: 1px solid rgba(34,211,238,0.26);
        animation: querion-pulse-ring 1.8s ease-in-out infinite;
    }

    .querion-dot {
        position: absolute;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: radial-gradient(circle, #ffffff 0%, var(--accent) 42%, rgba(34,211,238,0.15) 100%);
        box-shadow: 0 0 18px rgba(34,211,238,0.42);
        animation: querion-dot-orbit 1.8s linear infinite;
        top: 8px;
        left: 30px;
    }

    .querion-core {
        position: absolute;
        inset: 19px;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 35%, rgba(255,255,255,0.98), rgba(255,255,255,0.65) 24%, rgba(34,211,238,0.15) 65%, rgba(16,185,129,0.10) 100%);
        box-shadow:
            inset 0 0 16px rgba(255,255,255,0.22),
            0 0 20px rgba(16,185,129,0.12);
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
        opacity: 0.95;
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
        0%, 100% { transform: scale(0.98); opacity: 0.90; }
        50% { transform: scale(1.04); opacity: 1; }
    }

    @keyframes querion-pulse-ring {
        0%, 100% { opacity: 0.65; transform: scale(0.98); }
        50% { opacity: 1; transform: scale(1.03); }
    }

    @keyframes querion-bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.55; }
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
        timeout=180,
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


def search_depth_to_top_k(choice: str) -> int:
    mapping = {
        "Focused": 3,
        "Balanced": 5,
        "Thorough": 8,
    }
    return mapping.get(choice, 5)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

if "search_mode" not in st.session_state:
    st.session_state.search_mode = "Balanced"

health_ok, health_status = backend_health()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="querion-shell">
        <section class="querion-hero">
            <h1 class="querion-title">Querion<span>.</span></h1>
            <p class="querion-subtitle">
                Upload a PDF, ask a question, and get answers grounded in your own documents.
                The interface is built for mobile and desktop with a futuristic cyan and emerald theme.
            </p>
            <div class="querion-status-row">
                <div class="querion-pill">
                    <strong>Backend</strong>
                    <span>{"Online" if health_ok else f"Wake-up / unavailable · {health_status}"}</span>
                </div>
                <div class="querion-pill">
                    <strong>Mode</strong>
                    <span>PDF RAG</span>
                </div>
            </div>
        </section>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Upload / Settings
# ---------------------------------------------------------------------------
st.markdown('<div class="querion-divider"></div>', unsafe_allow_html=True)
st.markdown("### 📄 Knowledge Base")
st.markdown(
    '<p class="querion-help">Upload a PDF here. The controls stay visible on mobile and desktop.</p>',
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

search_mode = st.select_slider(
    "How thoroughly should Querion search?",
    options=["Focused", "Balanced", "Thorough"],
    value=st.session_state.search_mode,
    help="Focused searches fewer passages. Thorough searches more passages before answering.",
)
st.session_state.search_mode = search_mode
search_depth = search_depth_to_top_k(search_mode)

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
                f"({result.get('chunks', 0)} passages indexed)"
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
