from langgraph.graph import StateGraph, END
from agents.state import BharatBotState
from agents.nodes import (
    detect_language_node,
    retrieve_docs_node,
    generate_response_node
)
from agents.memory import get_memory


def build_graph():
    graph = StateGraph(BharatBotState)

    graph.add_node("detect_language", detect_language_node)
    graph.add_node("retrieve_docs", retrieve_docs_node)
    graph.add_node("generate_response", generate_response_node)

    graph.set_entry_point("detect_language")
    graph.add_edge("detect_language", "retrieve_docs")
    graph.add_edge("retrieve_docs", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile(checkpointer=get_memory())


bharatbot_app = build_graph()