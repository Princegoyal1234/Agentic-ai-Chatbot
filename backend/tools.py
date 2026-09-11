from langchain_core.tools import tool

from langchain_core.runnables import (
    RunnableConfig,
)

from langchain_community.tools import (
    DuckDuckGoSearchRun,
)

from .config import (
    VECTORSTORE_DIR,
)

from .rag import (
    embeddings,
    search_pdf,
)


# =====================================================
# PDF RAG TOOL
# =====================================================

@tool
def pdf_rag(
    query: str,
    config: RunnableConfig,
):
    """
    Search the uploaded PDF.

    Use this tool ONLY when the user asks
    specific questions about the uploaded PDF.
    """

    thread_id = (
        config[
            "configurable"
        ][
            "thread_id"
        ]
    )

    return search_pdf(
        query,
        thread_id,
    )


# =====================================================
# BASIC TOOLS
# =====================================================

@tool
def add(
    a: int,
    b: int,
) -> int:

    """Add two numbers."""

    return a + b


@tool
def multiply(
    a: int,
    b: int,
) -> int:

    """Multiply two numbers."""

    return a * b


# =====================================================
# WEB SEARCH
# =====================================================

search_tool = (
    DuckDuckGoSearchRun()
)


# =====================================================
# ALL TOOLS
# =====================================================

tools = [
    add,
    multiply,
    search_tool,
    pdf_rag,
]