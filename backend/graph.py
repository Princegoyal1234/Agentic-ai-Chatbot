from typing import (
    Annotated,
    TypedDict,
)

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import (
    SystemMessage,
)

from langchain_core.runnables import (
    RunnableConfig,
)

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.graph.message import (
    add_messages,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from langgraph.store.base import (
    BaseStore,
)
from dotenv import load_dotenv

from .tools import tools

from .memory import (
    remember_node,
)

from .database import (
    memory,
    store,
)


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant with memory capabilities.

If user-specific memory is available, use it to personalize
your responses based on what you know about the user.

The user's memory is:

{user_details_content}
"""


# =====================================================
# STATE
# =====================================================

class ChatState(TypedDict):

    messages: Annotated[
        list,
        add_messages,
    ]

load_dotenv()
# =====================================================
# LLM
# =====================================================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

llm_with_tools = (
    llm.bind_tools(
        tools
    )
)


# =====================================================
# CHAT NODE
# =====================================================

def chat_node(
    state: ChatState,
    config: RunnableConfig,
    *,
    store: BaseStore,
):

    user_id = (
        config[
            "configurable"
        ][
            "user_id"
        ]
    )

    namespace = (
        "user",
        user_id,
        "details",
    )

    items = store.search(
        namespace
    )

    user_details = (
        "\n".join(
            item.value.get(
                "data",
                ""
            )
            for item in items
        )
        if items
        else ""
    )

    system_msg = SystemMessage(
        content=
        SYSTEM_PROMPT_TEMPLATE.format(
            user_details_content=
            user_details or "(empty)"
        )
    )

    response = (
        llm_with_tools.invoke(
            [
                system_msg
            ]
            +
            state["messages"]
        )
    )

    return {
        "messages": [
            response
        ]
    }


# =====================================================
# GRAPH
# =====================================================

graph = StateGraph(
    ChatState
)

graph.add_node(
    "chat_node",
    chat_node
)

graph.add_node(
    "tools",
    ToolNode(tools)
)

graph.add_node(
    "remember",
    remember_node
)


# =====================================================
# EDGES
# =====================================================

graph.add_edge(
    START,
    "remember"
)

graph.add_edge(
    "remember",
    "chat_node"
)

graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

graph.add_edge(
    "tools",
    "chat_node"
)
graph.add_edge("chat_node",END)

# =====================================================
# COMPILE
# =====================================================

app = graph.compile(
    checkpointer=memory,
    store=store,
)