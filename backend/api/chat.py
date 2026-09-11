import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..services import get_stream


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):

    message: str
    thread_id: str
    user_id:str

@router.post("/")
def chat(request: ChatRequest):
    def generate():
        try:
            for mode, data in get_stream(
                request.message,
                request.thread_id,
                request.user_id
            ):

             # ==================================================
# 1. MESSAGE STREAM
# ==================================================

                if mode == "messages":

                    chunk, metadata = data

                    # ----------------------------------------------
                    # Get the LangGraph node that produced this chunk
                    # ----------------------------------------------

                    node = metadata.get(
                        "langgraph_node"
                    )

                    content = getattr(
                        chunk,
                        "content",
                        ""
                    ) or ""

                    message_type = getattr(
                        chunk,
                        "type",
                        ""
                    )

                    tool_calls = (
                        getattr(
                            chunk,
                            "tool_calls",
                            []
                        ) or []
                    )

                    tool_call_chunks = (
                        getattr(
                            chunk,
                            "tool_call_chunks",
                            []
                        ) or []
                    )

                    # ==================================================
                    # TOOL CALL
                    # ==================================================

                    if tool_calls or tool_call_chunks:

                        yield (
                            json.dumps({
                                "mode": "messages",
                                "event": "tool_call",

                                "content": "",

                                "tool_calls":
                                    tool_calls,

                                "tool_call_chunks":
                                    tool_call_chunks,

                                "metadata":
                                    metadata,
                            })
                            + "\n"
                        )

                        # Do not treat tool-call content as AI answer
                        continue

                    # ==================================================
                    # ONLY USER-FACING CHAT NODE
                    # ==================================================

                    if node != "chat_node":

                        continue

                    # ==================================================
                    # ONLY AI MESSAGE
                    # ==================================================

                    if message_type != "AIMessageChunk":

                        continue

                    # ==================================================
                    # IGNORE EMPTY CHUNKS
                    # ==================================================

                    if not content:

                        continue

                    # ==================================================
                    # SEND AI TOKEN TO FRONTEND
                    # ==================================================

                    yield (
                        json.dumps({
                            "mode": "messages",
                            "event": "token",

                            "content": content,

                            "type": message_type,

                            "metadata": metadata,
                        })
                        + "\n"
                    )
                # ==================================================
                # 2. GRAPH UPDATES
                # ==================================================

                elif mode == "updates":

                    clean_data = {}

                    for node_name, node_data in data.items():

                        # ------------------------------------------
                        # Non-dict node data
                        # ------------------------------------------

                        if not isinstance(
                            node_data,
                            dict
                        ):

                            clean_data[node_name] = node_data
                            continue


                        clean_node = {}

                        # ------------------------------------------
                        # Copy normal state values
                        # ------------------------------------------

                        for key, value in node_data.items():

                            if key != "messages":

                                clean_node[key] = value


                        # ------------------------------------------
                        # Serialize messages
                        # ------------------------------------------

                        if "messages" in node_data:

                            clean_messages = []

                            for message in node_data[
                                "messages"
                            ]:

                                if hasattr(
                                    message,
                                    "content"
                                ):

                                    clean_messages.append({

                                        "content":
                                            message.content,

                                        "type":
                                            getattr(
                                                message,
                                                "type",
                                                None
                                            ),

                                        "tool_calls":
                                            (
                                                getattr(
                                                    message,
                                                    "tool_calls",
                                                    []
                                                )
                                                or []
                                            ),

                                        "tool_call_chunks":
                                            (
                                                getattr(
                                                    message,
                                                    "tool_call_chunks",
                                                    []
                                                )
                                                or []
                                            ),
                                    })

                                else:

                                    clean_messages.append(
                                        message
                                    )


                            clean_node[
                                "messages"
                            ] = clean_messages


                        clean_data[
                            node_name
                        ] = clean_node


                    # ----------------------------------------------
                    # Send graph update
                    # ----------------------------------------------

                    yield (
                        json.dumps({
                            "mode": "updates",
                            "event": "graph_update",
                            "data": clean_data,
                        })
                        + "\n"
                    )


        except Exception as e:

            yield (
                json.dumps({
                    "mode": "error",
                    "event": "error",
                    "error": str(e),
                })
                + "\n"
            )


    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )