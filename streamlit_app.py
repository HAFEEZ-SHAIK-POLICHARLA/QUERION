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
    page_title="Querion",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Querion theming — presentation only. Nothing below this block touches
# the Inngest / Qdrant / OpenRouter wiring.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Hide only the hamburger menu, footer, and deploy button. */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ---- Sidebar is now permanent: no collapse/reopen control exists.
       The old toggle-visibility-forcing CSS block (reopen pill, hover/
       active/focus overrides, icon coloring) has been removed entirely —
       there's nothing left to toggle, so there's nothing left to fix.
       Both the "reopen when collapsed" control and the "collapse when
       expanded" control are hidden so no clickable affordance remains. ---- */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-headerNoPadding"] {
        display: none !important;
    }

    /* ---- Base light theme ---- */
    html, body, .stApp {
        background-color: transparent;
        color: #0d0d0d;
    }

    /* ---- Animated retrieval-themed background ----
       Layer 1: faint drifting grid = embedding / vector space
       Layer 2: soft pulsing colored nodes = semantic matches lighting up */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -2;
        background-color: #ffffff;
        background-image:
            linear-gradient(rgba(1, 121, 111, 0.05) 1px, transparent 6px),
            linear-gradient(90deg, rgba(33, 201, 187, 0.05) 1px, transparent 6px);
        background-size: 46px 46px;
        animation: querion-drift 60s linear infinite;
    }
    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        background-image:
            radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.10) 0, transparent 9%),
            radial-gradient(circle at 80% 25%, rgba(16, 185, 129, 0.08) 0, transparent 10%),
            radial-gradient(circle at 35% 78%, rgba(99, 102, 241, 0.09) 0, transparent 8%),
            radial-gradient(circle at 70% 85%, rgba(16, 185, 129, 0.07) 0, transparent 9%);
        animation: querion-pulse 12s ease-in-out infinite;
    }
    @keyframes querion-drift {
        from { background-position: 0 0, 0 0; }
        to   { background-position: 460px 460px, 460px 460px; }
    }
    @keyframes querion-pulse {
        0%, 100% { opacity: 0.55; }
        50%      { opacity: 1; }
    }

    /* ---- Sidebar: translucent so background shows through ---- */
    section[data-testid="stSidebar"] {
        background-color: rgba(249, 249, 249, 0.88);
        backdrop-filter: blur(6px);
        border-right: 1px solid #e5e5e5;
    }
    section[data-testid="stSidebar"] * {
        color: #0d0d0d;
    }

    /* ---- Main column ---- */
    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }

    /* ---- Querion header with intro animation ---- */
    .querion-header {
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .querion-header h1 {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        font-size: 4.15rem;
        color: #50E2D6 !important; 
        margin-bottom: 0.1rem;
        animation: querion-intro 0.9s ease-out;
    }
    .querion-subtext {
        text-align: center;
        color: #6e6e80;
        font-size: 1.25rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        animation: querion-intro 0.9s ease-out 0.15s;
        animation-fill-mode: both;
    }
    @keyframes querion-intro {
        from { opacity: 0; transform: translateY(-10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ---- Welcome card shown in empty chat state ---- */
    .querion-welcome {
    background-color: transparent;
    color: #353740;
    line-height: 1.55;
    font-size: 1.25rem;
    animation: querion-intro 0.9s ease-out 0.25s;
    animation-fill-mode: both;
    }

    /* ---- Chat messages: light ChatGPT style ----
       User = light gray bubble. Assistant = unboxed plain text. */
    div[data-testid="stChatMessage"] {
        background-color: transparent;
        border: none;
        padding: 0.6rem 0;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"])
        div[data-testid="stChatMessageContent"] {
        background-color: #f4f4f4;
        border-radius: 14px;
        padding: 0.8rem 1.05rem;
    }
    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"])
        div[data-testid="stChatMessageContent"] {
        background-color: transparent;
        padding: 0.4rem 0.2rem;
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
    div[data-testid="stChatMessageContent"] div,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] strong {
        color: #0d0d0d !important;
        line-height: 1.55;
    }

    /* ---- Chat input bar: make the FULL outer bar translucent glass-blur,
       not just the thin inner textarea. Send (arrow) button is untouched. ----
       Previous version used a risky :has() ancestor selector that matched
       too broad a parent and painted an unintended gray rectangle. Targeting
       the real fixed-bottom containers directly instead. */
    [data-testid="stBottom"] {
        background-color: rgba(255, 255, 255, 0.55) !important;
        backdrop-filter: blur(14px) !important;
        border-top: 1px solid #e5e5e5 !important;
    }
    [data-testid="stBottomBlockContainer"] {
        background-color: #01796F !important;
    }
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #0d0d0d !important;
        border: 1px solid #d9d9e3 !important;
        border-radius: 14px !important;
    }

    /* ---- Buttons ---- */
    /* ---- Send (arrow) button: white button, black arrow icon ---- */
button[data-testid="stChatInputSubmitButton"] {
    background-color: #ffffff !important;
    border: 1px solid #d9d9e3 !important;
}
button[data-testid="stChatInputSubmitButton"] svg {
    fill: #0d0d0d !important;
    color: #0d0d0d !important;
}
    .stButton button {
        background-color: #f4f4f4;
        color: #0d0d0d;
        border: 1px solid #d9d9e3;
        border-radius: 10px;
    }
    .stButton button:hover {
        background-color: #000000;
        border-color: #c9c9d3;
    }

    /* ---- File uploader ---- */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: rgba(255, 255, 255, 0.6);
        border: 1px dashed #d9d9e3;
        border-radius: 10px;
    }
    /* Fix 2: plain white button, black text, thin outline, no icon graphic */
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #ffffff !important;
        color: #0d0d0d !important;
        border: 1px solid #d9d9e3 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }
    section[data-testid="stFileUploaderDropzone"] button svg {
        display: none !important;
    }
    section[data-testid="stFileUploaderDropzone"] svg {
        display: none !important;
    }

    /* Fix 3: chunk selector (top_k number input) was unreadable dark —
       match it to the same white / thin-outline style as the upload button */
    div[data-testid="stNumberInput"] {
        background-color: transparent !important;
    }
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d9d9e3 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #0d0d0d !important;
        border: none !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #ffffff !important;
        color: #0d0d0d !important;
        border: none !important;
        border-left: 1px solid #d9d9e3 !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #0d0d0d !important;
    }

    .stCaption, small {
        color: #6e6e80 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(
        app_id="rag_app",
        event_key=os.getenv("INNGEST_EVENT_KEY")
    )

def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


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


async def send_rag_query_event(question: str, top_k: int):
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
    return os.getenv(
        "INNGEST_API_BASE",
        "https://api.inngest.com"
    )


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"

    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json()

    return data.get("data", [])


def wait_for_run_output(
    event_id: str,
    timeout_s: float = 120.0,
    poll_interval_s: float = 1.0,
):
    start = time.time()

    while True:
        runs = fetch_runs(event_id)

        if runs:
            run = runs[0]

            status = (run.get("status") or "").lower()

            if status == "completed":
                return run.get("output", {})

            if status in ("failed", "cancelled"):
                raise RuntimeError(
                    f"Function run {status}"
                )

        if time.time() - start > timeout_s:
            raise TimeoutError(
                f"Timed out waiting for run output for event {event_id}"
            )

        time.sleep(poll_interval_s)


# ---------------------------------------------------------------------------
# Session state for chat history (presentation only)
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str, "sources": list}

# ---------------------------------------------------------------------------
# Sidebar: PDF ingestion panel
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📄 Knowledge Base")
    st.caption("Upload PDFs to make them searchable.")

    uploaded = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if uploaded is not None and st.button("Ingest PDF", use_container_width=True):
        with st.spinner("Uploading and triggering ingestion..."):
            path = save_uploaded_pdf(uploaded)

            run_async(send_rag_ingest_event(path))

            time.sleep(0.3)

        st.success(f"Triggered ingestion for: {path.name}")

    st.divider()

    top_k = st.number_input(
        "Chunks to retrieve (top_k)",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main: Querion header + chat interface
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="querion-header">
        <h1>Querion</h1>
    </div>
    <p class="querion-subtext">Your documents, answered intelligently.</p>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        """
        <div class="querion-welcome">
            Querion turns your documents into a knowledge base you can talk to.
            Upload a PDF, ask anything, get grounded answers with sources.
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
                    st.write(f"- {s}")

question = st.chat_input("Message Querion...")

if question and question.strip():
    question = question.strip()

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Sending event and generating answer..."):
                event_id = run_async(
                    send_rag_query_event(
                        question,
                        int(top_k),
                    )
                )

                output = wait_for_run_output(event_id)

                if not isinstance(output, dict):
                    output = {}

                answer = output.get("answer", "")
                sources = output.get("sources", [])

            st.write(answer or "(No answer)")
            if sources:
                with st.expander("Sources"):
                    for s in sources:
                        st.write(f"- {s}")

        st.session_state.messages.append(
            {"role": "assistant", "content": answer or "(No answer)", "sources": sources}
        )

    except Exception as e:
        import traceback
        st.code(traceback.format_exc())
        st.error(str(e))
