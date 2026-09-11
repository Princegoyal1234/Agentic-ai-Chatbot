import streamlit as st
import uuid
import requests
API_URL="http://localhost:8000"
def get_chat_history(thread_id,user_id):

    response = requests.get(
        f"{API_URL}/threads/{thread_id}",
        params={
            "user_id":user_id
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("success"):

        raise Exception(
            data.get(
                "error",
                "Failed to load chat history"
            )
        )

    return data["history"]
# =========================================================
# THREAD HELPERS
# =========================================================

def upload_pdf(
    uploaded_file,
    thread_id,
):

    response = requests.post(
        f"{API_URL}/files/upload",

        data={
            "thread_id": thread_id,
        },

        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        },

        timeout=300,
    )

    print("STATUS CODE:", response.status_code)
    print("URL:", response.url)
    print("RESPONSE:", response.text)
    response.raise_for_status()

    data = response.json()

    if not data.get("success"):

        raise Exception(
            data.get(
                "error",
                "Failed to upload PDF"
            )
        )

    return data
def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):

    if thread_id not in st.session_state.chat_thread:
        st.session_state.chat_thread[thread_id] = "New Chat"


def reset_session():
    """
    Start a completely new conversation.
    """

    st.session_state.thread_id = generate_thread_id()

    st.session_state.messages = []

    # Reset uploader
    st.session_state.uploader_key += 1

    add_thread(
        st.session_state.thread_id
    )


# =========================================================
# LOAD CHAT HISTORY
# =========================================================

def load_chat_history(thread_id):

    st.session_state.messages = []

    history = get_chat_history(
        thread_id,
        st.session_state.user_id
    )
    for msg in history:

        st.session_state.messages.append(
            {
                "role": (
                    "user"
                    if msg["type"] == "human"
                    else "assistant"
                ),
                "content": msg["content"],
            }
        )


# =========================================================
# PDF UPLOAD
# =========================================================

def handle_pdf_upload():

    uploaded_file = st.file_uploader(
        "📄 Upload PDF",
        type=["pdf"],
        key=(
            f"pdf_uploader_"
            f"{st.session_state.uploader_key}"
        ),
    )

    current_thread = (
        st.session_state.thread_id
    )

    # Index only once per thread
    if (
        uploaded_file is not None
        and uploaded_file.name
        not in st.session_state.thread_pdfs[current_thread]
    ):

        with st.spinner(
            "📄 Indexing PDF..."
        ):

            upload_pdf(
                uploaded_file,
                current_thread,
            )

        st.session_state.thread_pdfs[current_thread].append(uploaded_file.name)

        st.success(
            "✅ PDF Indexed Successfully"
        )

    # Show uploaded PDF
    if (
        current_thread
        in st.session_state.thread_pdfs
    ):

        pdf_names = (
            st.session_state
            .thread_pdfs[current_thread]
        )

        for pdf_name in pdf_names:
            st.info(
                f"📄 {pdf_name}"
            )


# =========================================================
# CHAT HISTORY
# =========================================================

def display_chat_threads():

    for thread_id, title in reversed(
        list(
            st.session_state
            .chat_thread
            .items()
        )
    ):

        if st.button(
            title,
            key=thread_id,
            use_container_width=True,
        ):

            st.session_state.thread_id = (
                thread_id
            )

            load_chat_history(
                thread_id
            )

            st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        st.title("💬 Chats")

        # =================================================
        # NEW CHAT
        # =================================================

        if st.button(
            "➕ New Chat",
            use_container_width=True,
        ):

            reset_session()

            st.rerun()

        st.divider()

        # =================================================
        # PDF
        # =================================================

        handle_pdf_upload()

        st.divider()

        # =================================================
        # CHAT HISTORY
        # =================================================

        display_chat_threads()