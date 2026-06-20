from __future__ import annotations

import time
from typing import Any

import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "https://querion-backend-1.onrender.com").rstrip("/")
MAX_UPLOAD_MB = 50

st.set_page_config(page_title="Querion", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --surface: rgba(255,255,255,0.97);
        --stroke: rgba(16,185,129,0.14);
        --text-main: #10222d;
        --text-soft: #5f7680;
        --accent: #22d3ee;
        --accent-2: #10b981;
        --shadow: 0 18px 50px rgba(16,185,129,0.08), 0 10px 32px rgba(34,211,238,0.06);
    }
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f8fffe 0%, #f1fffd 52%, #e7fffb 100%) !important;
    }
    .block-container { max-width: 1040px; padding-top: 1.1rem; padding-bottom: 6rem; }
    .querion-title { font-size: clamp(2.1rem, 5.5vw, 3.6rem); font-weight: 900; letter-spacing: -0.04em; color: var(--text-main); margin: 0; }
    .querion-title span { color: var(--accent); }
    .querion-subtitle { color: var(--text-soft); font-size: 1.02rem; line-height: 1.6; margin-top: 0.5rem; max-width: 70ch; }
    .querion-pill { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.45rem 0.8rem; border-radius: 999px;
        background: var(--surface); border: 1px solid var(--stroke); color: var(--text-soft); font-size: 0.88rem; }
    .querion-pill strong { color: var(--text-main); }
    .querion-card { background: var(--surface); border: 1px solid var(--stroke); border-radius: 18px; box-shadow: var(--shadow); padding: 1rem 1.1rem; }
    .querion-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(34,211,238,0.3), rgba(16,185,129,0.32), transparent); margin: 0.8rem 0; }
    .stButton button { border-radius: 12px !important; font-weight: 700 !important; }
    div[data-testid="stChatMessageContent"] { background: var(--surface) !important; border: 1px solid var(--stroke) !important; border-radius: 16px !important; }
    div[data-testid="stChatInput"] textarea { font-size: 16px !important; }
    @media (max-width: 768px) {
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30)
def backend_health() -> bool:
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=5).ok
    except Exception:
        return False


def err_message(response: requests.Response) -> str:
    try:
        data = response.json()
        return data.get("error") or data.get("detail") or str(data)
    except Exception:
        return response.text.strip() or f"HTTP {response.status_code}"


def start_upload(uploaded_file) -> str:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
    if not resp.ok:
        raise RuntimeError(err_message(resp))
    return resp.json()["job_id"]


def poll_job(job_id: str) -> dict:
    resp = requests.get(f"{BACKEND_URL}/upload/status/{job_id}", timeout=15)
    if not resp.ok:
        raise RuntimeError(err_message(resp))
    return resp.json()


def query_backend(question: str, top_k: int, history: list[dict]) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/query",
        json={"question": question, "top_k": top_k, "history": history},
        timeout=90,
    )
    if not resp.ok:
        raise RuntimeError(err_message(resp))
    return resp.json()


def fetch_kb_info() -> dict:
    try:
        resp = requests.get(f"{BACKEND_URL}/knowledge-base", timeout=15)
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return {"sources": [], "total_chunks": 0}


def clear_kb():
    requests.post(f"{BACKEND_URL}/knowledge-base/clear", timeout=20)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
st.session_state.setdefault("messages", [])
st.session_state.setdefault("search_mode", "Balanced")
st.session_state.setdefault("size_warning", "")

DEPTH = {"Focused": 3, "Balanced": 5, "Thorough": 8}

# ---------------------------------------------------------------------------
# Sidebar — Knowledge Base
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📚 Knowledge Base")
    kb = fetch_kb_info()
    if kb["sources"]:
        st.caption(f"{len(kb['sources'])} document(s) · {kb['total_chunks']} passages indexed")
        for src in kb["sources"]:
            st.markdown(f"• {src}")
    else:
        st.caption("No documents indexed yet.")

    if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
        clear_kb()
        st.cache_data.clear()
        st.success("Knowledge base cleared.")
        st.rerun()

    st.markdown("---")
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.session_state.search_mode = st.select_slider(
        "Search depth", options=list(DEPTH.keys()), value=st.session_state.search_mode
    )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
healthy = backend_health()
st.markdown(
    f"""
    <h1 class="querion-title">Querion<span>.</span></h1>
    <p class="querion-subtitle">Upload PDFs and ask questions grounded in your own documents.</p>
    <div class="querion-pill"><strong>Backend</strong>&nbsp;{"🟢 Online" if healthy else "🟡 Waking up..."}</div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="querion-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Upload — supports multiple PDFs, one after another
# ---------------------------------------------------------------------------
st.markdown("### 📄 Add a document")
uploaded_file = st.file_uploader(f"PDF, up to {MAX_UPLOAD_MB}MB", type=["pdf"], label_visibility="collapsed")

if uploaded_file is not None:
    size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        st.error(f"⚠️ This file is {size_mb:.1f}MB. The limit is {MAX_UPLOAD_MB}MB — please upload a smaller PDF.")
    else:
        st.caption(f"Selected: {uploaded_file.name} ({size_mb:.1f}MB)")
        if st.button("Ingest PDF", type="primary", use_container_width=True):
            try:
                job_id = start_upload(uploaded_file)
                progress_bar = st.progress(0, text="Starting...")
                status_box = st.empty()

                while True:
                    status = poll_job(job_id)
                    state = status.get("status")

                    if state == "duplicate":
                        progress_bar.empty()
                        st.info(f"ℹ️ {status.get('message', 'This PDF is already indexed.')}")
                        break

                    if state == "error":
                        progress_bar.empty()
                        st.error(f"Upload failed: {status.get('error', 'Unknown error')}")
                        break

                    if state == "done":
                        progress_bar.progress(1.0, text="Done!")
                        st.success(f"✅ {status.get('message', 'Indexed successfully.')}")
                        st.cache_data.clear()
                        time.sleep(0.6)
                        st.rerun()
                        break

                    total = max(status.get("total_pages", 1), 1)
                    current = status.get("current_page", 0)
                    pct = min(current / total, 0.99)
                    progress_bar.progress(pct, text=status.get("message", "Processing..."))
                    time.sleep(1)

            except Exception as exc:
                st.error(f"Upload failed: {exc}")

st.markdown('<div class="querion-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        """
        <div class="querion-card">
            <strong>Start the conversation</strong>
            <p style="color:#5f7680; margin-top:0.4rem;">
                Upload one or more PDFs above, then ask something like
                "What is this document about?" or "Compare the two reports."
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.write(f"• {s}")

question = st.chat_input("Ask Querion about your documents…")

if question and question.strip():
    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1][-6:]
    ]

    with st.spinner("Querion is searching your documents..."):
        try:
            result = query_backend(question, DEPTH[st.session_state.search_mode], history)
            answer = (result.get("answer") or "").strip() or "(No answer)"
            sources = result.get("sources", [])
            cached_note = " _(cached answer)_" if result.get("cached") else ""

            with st.chat_message("assistant"):
                st.write(answer + cached_note)
                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            st.write(f"• {s}")

            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

        except Exception as exc:
            error_text = f"Query failed: {exc}"
            with st.chat_message("assistant"):
                st.error(error_text)
            st.session_state.messages.append({"role": "assistant", "content": error_text, "sources": []})
