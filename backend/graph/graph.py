from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy

from graph.state import GraphState, WriterInput
from graph.nodes.architect import architect_node, hitl_node
from graph.nodes.writer import writer_node
from graph.nodes.assembler import assembler_node

# Retry up to 3 times with exponential backoff for transient LLM API errors
_WRITER_RETRY = RetryPolicy(max_attempts=3, backoff_factor=2.0)
_ARCHITECT_RETRY = RetryPolicy(max_attempts=2, backoff_factor=2.0)


def route_after_hitl(state: GraphState) -> str:
    if state.get("user_feedback") and state.get("status") != "writing":
        return "architect_node"
    return "route_writers"


def route_to_writers(state: GraphState) -> list[Send]:
    """Fan-out: one Send per subsection → parallel execution."""
    return [
        Send("writer_node", WriterInput(
            user_profile=state["user_profile"],
            section=section,
            book_outline=state["book_outline"],
        ))
        for section in state["sections_to_write"]
    ]


def build_graph(checkpointer=None):
    builder = StateGraph(GraphState)

    builder.add_node("architect_node", architect_node, retry_policy=_ARCHITECT_RETRY)
    builder.add_node("hitl_node", hitl_node)
    builder.add_node("writer_node", writer_node, retry_policy=_WRITER_RETRY)
    builder.add_node("assembler_node", assembler_node)

    builder.add_edge(START, "architect_node")
    builder.add_edge("architect_node", "hitl_node")

    builder.add_conditional_edges(
        "hitl_node",
        route_after_hitl,
        {"architect_node": "architect_node", "route_writers": "route_writers"},
    )

    builder.add_node("route_writers", lambda s: {})
    builder.add_conditional_edges("route_writers", route_to_writers, ["writer_node"])

    builder.add_edge("writer_node", "assembler_node")
    builder.add_edge("assembler_node", END)

    return builder.compile(checkpointer=checkpointer)


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        from graph.checkpointer import get_checkpointer
        _graph = build_graph(checkpointer=get_checkpointer())
    return _graph
