import streamlit as st
from langchain_core.messages import AIMessage
import requests
import json
API_URL="http://localhost:8000"
def get_chat_stream(
    message,
    thread_id,
    user_id,
):

    response = requests.post(
        f"{API_URL}/chat/",
        json={
            "message": message,
            "thread_id": thread_id,
            "user_id": user_id,
        },
        stream=True,
        timeout=300,
    )

    response.raise_for_status()
    # Read streaming response
    for line in response.iter_lines(
        decode_unicode=True
    ):

        if not line:
            continue

        try:

            data = json.loads(line)

            yield data

        except json.JSONDecodeError:

            continue
# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

def display_chat_history():

   for message in st.session_state.messages:

    role = message.get(
        "role",
        ""
    )

    content = message.get(
        "content",
        ""
    )

    # ==========================================
    # IGNORE TOOL / CONTEXT MESSAGES
    # ==========================================

    if role in [
        "tool",
        "ToolMessage"
    ]:
        continue

    # ==========================================
    # IGNORE EMPTY MESSAGES
    # ==========================================

    if not content:
        continue

    # ==========================================
    # DISPLAY CHAT MESSAGE
    # ==========================================

    with st.chat_message(role):

        st.markdown(
            content
        )

# =========================================================
# STREAM LANGGRAPH RESPONSE
# =========================================================


def stream_response(
    prompt,
    thread_id,
    user_id,
):

    placeholder = st.empty()

    final = ""

    tool_status = None

    stream = get_chat_stream(
        prompt,
        thread_id,
        user_id,
    )

    for event in stream:

        mode = event.get("mode")
        event_type = event.get("event")

        # =================================================
        # ERROR
        # =================================================

        if mode == "error":

            st.error(
                event.get(
                    "error",
                    "Something went wrong."
                )
            )

            continue


        # =================================================
        # MESSAGE STREAM
        # =================================================

        if mode == "messages":

            # =================================================
            # NORMAL AI TOKEN
            # =================================================

            if event_type == "token":

                content = event.get(
                    "content",
                    ""
                )

                metadata = event.get(
                    "metadata",
                    {}
                )

                node = metadata.get(
                    "langgraph_node"
                )

                # ---------------------------------------------
                # Ignore internal remember node
                # ---------------------------------------------

                if node == "remember":
                    continue

                # ---------------------------------------------
                # Ignore empty content
                # ---------------------------------------------

                if not content:
                    continue

                # ---------------------------------------------
                # STREAM AI RESPONSE
                # ---------------------------------------------

                final += content

                placeholder.markdown(
                    final
                )


            # =================================================
            # TOOL CALL
            # =================================================

            elif event_type == "tool_call":

                tool_calls = event.get(
                    "tool_calls",
                    []
                )

                tool_call_chunks = event.get(
                    "tool_call_chunks",
                    []
                )

                # ---------------------------------------------
                # Prefer complete tool_calls
                # ---------------------------------------------

                if tool_calls:

                    tool = tool_calls[0]

                    tool_name = tool.get(
                        "name",
                        "unknown"
                    )

                    tool_args = tool.get(
                        "args",
                        {}
                    )

                    # -----------------------------------------
                    # Close previous status if any
                    # -----------------------------------------

                    if tool_status is not None:

                        tool_status.update(
                            label="Previous tool completed",
                            state="complete"
                        )

                    # -----------------------------------------
                    # Create tool status
                    # -----------------------------------------

                    tool_status = st.status(
                        f"🔧 Calling `{tool_name}`...",
                        expanded=True
                    )

                    if tool_args:

                        tool_status.json(
                            tool_args
                        )

                # ---------------------------------------------
                # Tool call chunks
                # ---------------------------------------------

                elif tool_call_chunks:

                    chunk = tool_call_chunks[0]

                    tool_name = chunk.get(
                        "name"
                    )

                    if tool_name:

                        if tool_status is not None:

                            tool_status.update(
                                label="Previous tool completed",
                                state="complete"
                            )

                        tool_status = st.status(
                            f"🔧 Calling `{tool_name}`...",
                            expanded=True
                        )


        # =================================================
        # GRAPH UPDATES
        # =================================================

        elif mode == "updates":

            if event_type != "graph_update":
                continue

            data = event.get(
                "data",
                {}
            )

            if not isinstance(
                data,
                dict
            ):
                continue


            # =================================================
            # CHAT NODE
            # =================================================

            if "chat_node" in data:

                chat_node = data[
                    "chat_node"
                ]

                if not isinstance(
                    chat_node,
                    dict
                ):
                    continue

                messages = chat_node.get(
                    "messages",
                    []
                )

                if not messages:
                    continue

                message = messages[-1]

                if not isinstance(
                    message,
                    dict
                ):
                    continue

                tool_calls = message.get(
                    "tool_calls",
                    []
                )

                # ---------------------------------------------
                # Tool call found in graph update
                # ---------------------------------------------

                if tool_calls:

                    tool = tool_calls[0]

                    tool_name = tool.get(
                        "name",
                        "unknown"
                    )

                    tool_args = tool.get(
                        "args",
                        {}
                    )

                    # Avoid creating duplicate status
                    if tool_status is None:

                        tool_status = st.status(
                            f"🔧 Calling `{tool_name}`...",
                            expanded=True
                        )

                        if tool_args:

                            tool_status.json(
                                tool_args
                            )


            # =================================================
            # TOOLS NODE
            # =================================================

            if "tools" in data:

                tools_node = data[
                    "tools"
                ]

                if not isinstance(
                    tools_node,
                    dict
                ):
                    continue

                messages = tools_node.get(
                    "messages",
                    []
                )

                if messages:

                    tool_message = messages[-1]

                    # -----------------------------------------
                    # Tool completed
                    # -----------------------------------------

                    if tool_status is not None:

                        tool_status.update(
                            label="✅ Tool completed",
                            state="complete"
                        )

                        tool_status = None


    # =================================================
    # FINISH
    # =================================================

    if tool_status is not None:

        tool_status.update(
            label="✅ Completed",
            state="complete"
        )

    return final
# =========================================================
# CHAT INTERFACE
# =========================================================

def render_chat():

    # Display old messages
    display_chat_history()

    # Chat input
    prompt = st.chat_input(
        "Type your message..."
    )

    if not prompt:
        return

    thread_id = (
        st.session_state.thread_id
    )

    user_id = (
        st.session_state.user_id
    )

    # =====================================================
    # STORE USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # =====================================================
    # GENERATE CHAT TITLE
    # =====================================================

    if (
        st.session_state.chat_thread[
            thread_id
        ]
        == "New Chat"
    ):

        st.session_state.chat_thread[
            thread_id
        ] = prompt[:30]

    # =====================================================
    # DISPLAY USER MESSAGE
    # =====================================================

    with st.chat_message("user"):

        st.markdown(prompt)

    # =====================================================
    # ASSISTANT RESPONSE
    # =====================================================

    with st.chat_message("assistant"):

        final = stream_response(
            prompt,
            thread_id,
            user_id,
        )

    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final,
        }
    )

    st.rerun()