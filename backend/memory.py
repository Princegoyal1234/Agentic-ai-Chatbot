import uuid

from typing import List

from pydantic import (
    BaseModel,
    Field,
)

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import (
    SystemMessage,
)

from langgraph.graph import MessagesState

from langgraph.store.base import (
    BaseStore,
)

from langchain_core.runnables import (
    RunnableConfig,
)


# =====================================================
# MEMORY LLM
# =====================================================

memory_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


# =====================================================
# MEMORY SCHEMAS
# =====================================================

class MemoryItem(BaseModel):

    text: str = Field(
        description="Atomic user memory"
    )

    is_new: bool = Field(
        description="True if new, false if duplicate"
    )


class MemoryDecision(BaseModel):

    should_write: bool

    memories: List[
        MemoryItem
    ] = Field(
        default_factory=list
    )


# =====================================================
# STRUCTURED OUTPUT
# =====================================================

memory_extractor = (
    memory_llm
    .with_structured_output(
        MemoryDecision
    )
)


# =====================================================
# MEMORY PROMPT
# =====================================================

MEMORY_PROMPT = """
You are responsible for updating and maintaining accurate user memory.

CURRENT USER DETAILS (existing memories):
{user_details_content}

TASK:

- Review the user's latest message.
- Extract user-specific info worth storing long-term
  (identity, stable preferences, ongoing projects/goals).
- For each extracted item, set is_new=true ONLY if
  it adds NEW information compared to CURRENT USER DETAILS.
- If it is basically the same meaning as something already
  present, set is_new=false.
- Keep each memory as a short atomic sentence.
- No speculation; only facts stated by the user.
- If there is nothing memory-worthy, return should_write=false
  and an empty list.
"""


# =====================================================
# REMEMBER NODE
# =====================================================

def remember_node(
    state: MessagesState,
    config: RunnableConfig,
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

    existing = (
        "\n".join(
            item.value.get(
                "data",
                ""
            )
            for item in items
        )
        if items
        else "(empty)"
    )

    last_text = (
        state["messages"][-1]
        .content
    )

    decision = (
        memory_extractor.invoke(
            [
                SystemMessage(
                    content=
                    MEMORY_PROMPT.format(
                        user_details_content=
                        existing
                    )
                ),
                {
                    "role": "user",
                    "content": last_text,
                },
            ]
        )
    )

    if decision.should_write:

        for mem in decision.memories:

            if (
                mem.is_new
                and mem.text.strip()
            ):

                store.put(
                    namespace,
                    str(uuid.uuid4()),
                    {
                        "data":
                            mem.text.strip()
                    },
                )

    return {}