from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from config.settings import DATABASE_URL

_checkpointer = None


def get_memory():
    global _checkpointer
    if _checkpointer is None:
        pool = ConnectionPool(conninfo=DATABASE_URL, max_size=10, kwargs={"autocommit": True})
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        _checkpointer = checkpointer
    return _checkpointer
