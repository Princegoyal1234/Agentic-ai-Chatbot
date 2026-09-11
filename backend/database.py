import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.postgres import PostgresStore

from .config import (
    DB_PATH,
    POSTGRES_URI,
)


# =====================================================
# SQLITE CHECKPOINTER
# =====================================================

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False,
)

memory = SqliteSaver(
    conn
)


# =====================================================
# POSTGRES LONG TERM MEMORY
# =====================================================

store_cm = PostgresStore.from_conn_string(
    POSTGRES_URI
)

store = store_cm.__enter__()

store.setup()

import atexit


atexit.register(
    store_cm.__exit__,
    None,
    None,
    None,
)