from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from graph.state import GraphState, WriterInput
from graph.nodes.architect import architect_node, hitl_node
from graph.nodes.writer import writer_node
from graph.nodes.assembler import assembler_node


def route_after_hitl(state: GraphState) -> str:
    """After HITL node: if user provided feedback → regenerate; if approved → write."""
    if state.get("user_feedback") and state.get("status") != "writing":
        return "architect_node"
    return "route_writers"


def route_to_writers(state: GraphState) -> list[Send]:
    """Fan-out: dispatches one Send per section to writer_node (parallel execution)."""
    return [
        Send("writer_node", WriterInput(
            user_profile=state["user_profile"],
            section=section,
        ))
        for section in state["sections_to_write"]
    ]


def build_graph(checkpointer=None):
    """Builds and compiles the biohacking book generation graph."""
    builder = StateGraph(GraphState)

    builder.add_node("architect_node", architect_node)
    builder.add_node("hitl_node", hitl_node)
    builder.add_node("writer_node", writer_node)
    builder.add_node("assembler_node", assembler_node)

    builder.add_edge(START, "architect_node")
    builder.add_edge("architect_node", "hitl_node")

    builder.add_conditional_edges(
        "hitl_node",
        route_after_hitl,
        {"architect_node": "architect_node", "route_writers": "route_writers"},
    )

    # Fan-out node: routes to parallel writers via Send()
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
