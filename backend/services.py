from langchain_core.messages import (
    HumanMessage,
)
import sqlite3

from .config import DB_PATH

from .graph import app


def get_stream( prompt,  thread_id, user_id,):
    stream = app.stream(
        {
            "messages": [
                HumanMessage(
                    content=prompt
                )
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id,
            },
            "metadata": {
                "thread_id": thread_id,
                "user_id": user_id,
            },
            "run_name": "chat_turn",
        },
        stream_mode=[
            "messages",
            "updates",
        ],
    )

    for item in stream:
        yield item

def get_chat_history(thread_id,user_id):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    state = app.get_state(config)
    if not state.values:
        return []
    return state.values["messages"]


def get_chat_threads(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    print("Tables:", cursor.fetchall())

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='checkpoints'
    """)

    if cursor.fetchone() is None:
        print("No checkpoints table found.")
        conn.close()
        return {}

    cursor.execute("""
        SELECT DISTINCT thread_id
        FROM checkpoints
    """)

    rows = cursor.fetchall()

    print(rows)

    thread_ids = [row[0] for row in rows]

    conn.close()
    chat_threads = {}
    
    for thread_id in thread_ids:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_id": user_id
                }
            }
    
            state = app.get_state(config)
    
            if "messages" in state.values and state.values["messages"]:
                # Use the first user message as the title
                title = state.values["messages"][0].content[:30]
            else:
                title = "New Chat"
    
            chat_threads[thread_id] = title
    
    return chat_threads
