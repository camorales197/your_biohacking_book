import os
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """Returns the LangGraph checkpointer. Uses SQLite in production, MemorySaver in tests."""
    db_path = os.getenv("CHECKPOINT_DB_PATH", "./checkpoints.db")

    # Use MemorySaver if running in test mode
    if os.getenv("TESTING") == "true" or db_path == ":memory:":
        return MemorySaver()

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        return SqliteSaver.from_conn_string(db_path)
    except ImportError:
        # langgraph-checkpoint-sqlite not installed — fall back to in-memory
        return MemorySaver()
