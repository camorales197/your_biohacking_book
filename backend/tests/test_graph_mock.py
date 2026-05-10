"""
Full graph integration test using FakeLLM — no real API calls.
Run: TESTING=true python -m pytest tests/test_graph_mock.py -v
"""
import os
import pytest

os.environ["OPENROUTER_API_KEY"] = "mock"
os.environ["TESTING"] = "true"

from langgraph.types import Command

from graph.state import GraphState, UserProfile
from graph.graph import build_graph
from graph.checkpointer import get_checkpointer


SAMPLE_PROFILE = UserProfile(
    age=35,
    sex="hombre",
    location="Madrid, España",
    health_issues=["resistencia a la insulina"],
    lifestyle="Trabajo de oficina, sedentario, duerme 6 horas",
    goals=["más energía", "perder grasa"],
    other_info="",
    sleep_hours=6.0,
    exercise_frequency="1-2x/semana",
    diet_type="omnívoro",
    stress_level="moderado",
    energy_level="bajo",
)

INITIAL_STATE = GraphState(
    session_token="test-session-token",
    user_email="test@example.com",
    user_profile=SAMPLE_PROFILE,
    book_outline=None,
    sections_to_write=[],
    written_sections=[],
    final_book=None,
    pdf_path=None,
    user_feedback=None,
    status="outlining",
    email_sent=False,
)


def make_graph():
    return build_graph(checkpointer=get_checkpointer())


def test_graph_compiles():
    g = make_graph()
    assert g is not None
    assert "architect_node" in g.nodes
    assert "hitl_node" in g.nodes
    assert "writer_node" in g.nodes
    assert "assembler_node" in g.nodes


def test_graph_runs_to_interrupt():
    """Graph should run architect node, commit outline, then pause at hitl_node interrupt."""
    g = make_graph()
    config = {"configurable": {"thread_id": "test-thread-1"}}

    g.invoke(INITIAL_STATE, config=config)

    snapshot = g.get_state(config)
    state = snapshot.values

    # Architect ran and committed outline to state before interrupt
    assert state["book_outline"] is not None
    assert "chapters" in state["book_outline"]
    assert len(state["sections_to_write"]) > 0
    assert state["status"] == "awaiting_approval"

    # Graph is paused at hitl_node
    assert snapshot.next == ("hitl_node",)


def test_graph_resumes_after_approval():
    """After approval, all sections should be written and book assembled."""
    g = make_graph()
    config = {"configurable": {"thread_id": "test-thread-2"}}

    # Run to interrupt
    g.invoke(INITIAL_STATE, config=config)

    # Resume with approval
    g.invoke(Command(resume={"approved": True, "feedback": ""}), config=config)

    state = g.get_state(config).values
    assert state["status"] == "done"
    assert state["final_book"] is not None
    assert len(state["written_sections"]) == len(state["sections_to_write"])


def test_architect_flattens_outline_correctly():
    """Flattened sections should have correct IDs and all required fields."""
    g = make_graph()
    config = {"configurable": {"thread_id": "test-thread-3"}}

    g.invoke(INITIAL_STATE, config=config)
    state = g.get_state(config).values

    sections = state["sections_to_write"]
    assert len(sections) > 0

    for s in sections:
        assert s["id"].startswith("ch")
        assert s["chapter"]
        assert s["section"]
        assert s["title"]
        assert s["focus"] in {
            "Acciones concretas",
            "Ciencia detrás del hábito",
            "Protocolo de implementación",
        }
        assert s["content"] is None  # Not yet written


def test_feedback_loop_regenerates():
    """Graph should pause again at hitl_node when feedback is provided (not approved)."""
    g = make_graph()
    config = {"configurable": {"thread_id": "test-thread-4"}}

    g.invoke(INITIAL_STATE, config=config)
    state_before = g.get_state(config).values
    assert state_before["book_outline"] is not None

    # Reject with feedback — triggers regeneration
    g.invoke(Command(resume={"approved": False, "feedback": "Add more sleep content"}), config=config)

    # Should pause again at hitl_node with new outline
    snapshot_after = g.get_state(config)
    state_after = snapshot_after.values
    assert state_after["book_outline"] is not None
    assert snapshot_after.next == ("hitl_node",)


def test_assembled_book_has_content():
    """Final book should have Markdown content with headers."""
    g = make_graph()
    config = {"configurable": {"thread_id": "test-thread-5"}}

    g.invoke(INITIAL_STATE, config=config)
    g.invoke(Command(resume={"approved": True, "feedback": ""}), config=config)

    state = g.get_state(config).values
    book = state["final_book"]
    assert book is not None
    assert "# " in book   # Has a top-level heading
    assert "## " in book  # Has chapter headings
