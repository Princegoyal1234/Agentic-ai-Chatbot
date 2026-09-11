import streamlit as st
import requests

from frontend.chat_module import (
    render_chat,
)

from frontend.sidebar_module import (
    render_sidebar,
    generate_thread_id,
    add_thread,
)
API_URL = "http://localhost:8000"

def get_chat_threads(user_id: str):
    try:
        response = requests.get(
            f"{API_URL}/threads/",
            timeout=10,
           params={
                "user_id": user_id
            },
        )

        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise Exception(
                data.get(
                    "error",
                    "Failed to get chat threads"
                )
            )

        return data.get(
            "threads",
            {}
        )

    except requests.exceptions.RequestException as e:

        raise Exception(
            f"Unable to connect to backend: {e}"
        )
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LangGraph RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)


st.title("🤖 LangGraph RAG Chatbot")


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "thread_id" not in st.session_state:

    st.session_state.thread_id = (
        generate_thread_id()
    )


if "user_id" not in st.session_state:

    st.session_state.user_id = "user1"


if "chat_thread" not in st.session_state:

    st.session_state.chat_thread = (
        get_chat_threads(
            st.session_state.user_id
        )
    )

if "thread_pdfs" not in st.session_state:
    st.session_state.thread_pdfs = {}

thread_id = st.session_state.thread_id

if thread_id not in st.session_state.thread_pdfs:
    st.session_state.thread_pdfs[thread_id] = []
    
if "uploader_key" not in st.session_state:

    st.session_state.uploader_key = 0


# =========================================================
# CURRENT THREAD
# =========================================================

add_thread(
    st.session_state.thread_id
)


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()


# =========================================================
# CHAT
# =========================================================

render_chat()