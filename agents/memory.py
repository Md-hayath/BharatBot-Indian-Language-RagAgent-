import os
from langgraph.checkpoint.memory import MemorySaver

def get_memory():
    os.makedirs("data", exist_ok=True)
    return MemorySaver()