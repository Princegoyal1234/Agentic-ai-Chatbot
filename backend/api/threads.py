# api/threads.py

from fastapi import APIRouter

from ..services import get_chat_threads
from ..services import get_chat_history

router = APIRouter(
    prefix="/threads",
    tags=["Threads"],
)


@router.get("/")
def get_threads(user_id:str):

    try:

        threads = get_chat_threads(user_id)

        return {
            "success": True,
            "threads": threads,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }

@router.get("/{thread_id}")
def get_thread_history(
    thread_id: str,
    user_id:str,
):

    try:

        history = get_chat_history(
            thread_id,user_id
        )

        return {
            "success": True,
            "thread_id": thread_id,
            "history": history,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }