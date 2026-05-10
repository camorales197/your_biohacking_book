import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from langgraph.types import Command
from pydantic import BaseModel, EmailStr

from graph.state import UserProfile, GraphState
from graph.graph import get_graph

router = APIRouter(prefix="/api")


# ── Request / Response schemas ────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    email: EmailStr
    age: int
    sex: str
    location: str
    health_issues: list[str]
    lifestyle: str
    goals: list[str]
    other_info: str = ""


class GenerateResponse(BaseModel):
    thread_id: str
    status: str


class StatusResponse(BaseModel):
    status: str
    outline: Optional[dict] = None
    sections_count: Optional[int] = None
    written_count: Optional[int] = None
    email_sent: Optional[bool] = None


class ApproveRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


class BookResponse(BaseModel):
    thread_id: str
    title: str
    content: str
    email_sent: bool


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate_book(req: GenerateRequest):
    """Start a new book generation run. Returns thread_id for polling."""
    thread_id = str(uuid.uuid4())
    config = _get_thread_config(thread_id)

    profile = UserProfile(
        age=req.age,
        sex=req.sex,
        location=req.location,
        health_issues=req.health_issues,
        lifestyle=req.lifestyle,
        goals=req.goals,
        other_info=req.other_info,
    )

    initial_state = GraphState(
        user_email=str(req.email),
        user_profile=profile,
        book_outline=None,
        sections_to_write=[],
        written_sections=[],
        final_book=None,
        user_feedback=None,
        status="outlining",
        email_sent=False,
    )

    graph = get_graph()
    await graph.ainvoke(initial_state, config=config)

    return GenerateResponse(thread_id=thread_id, status="awaiting_approval")


@router.get("/status/{thread_id}", response_model=StatusResponse)
async def get_status(thread_id: str):
    """Poll current graph state for a given thread."""
    graph = get_graph()
    snapshot = graph.get_state(_get_thread_config(thread_id))

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")

    state: GraphState = snapshot.values

    return StatusResponse(
        status=state.get("status", "unknown"),
        outline=state.get("book_outline"),
        sections_count=len(state.get("sections_to_write", [])),
        written_count=len(state.get("written_sections", [])),
        email_sent=state.get("email_sent"),
    )


@router.post("/approve/{thread_id}", response_model=GenerateResponse)
async def approve_outline(thread_id: str, req: ApproveRequest):
    """Resume graph after human review. approved=True → writing; False → regeneration."""
    graph = get_graph()
    config = _get_thread_config(thread_id)

    snapshot = graph.get_state(config)
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")

    resume_value = {"approved": req.approved, "feedback": req.feedback or ""}
    await graph.ainvoke(Command(resume=resume_value), config=config)

    state: GraphState = graph.get_state(config).values
    return GenerateResponse(thread_id=thread_id, status=state.get("status", "unknown"))


@router.get("/book/{thread_id}", response_model=BookResponse)
async def get_book(thread_id: str):
    """Returns the final assembled book Markdown once generation is complete."""
    graph = get_graph()
    snapshot = graph.get_state(_get_thread_config(thread_id))

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")

    state: GraphState = snapshot.values

    if state.get("status") != "done":
        raise HTTPException(status_code=202, detail="Book not ready yet")

    outline = state.get("book_outline") or {}
    return BookResponse(
        thread_id=thread_id,
        title=outline.get("title", "Tu Libro de Biohacking"),
        content=state.get("final_book", ""),
        email_sent=state.get("email_sent", False),
    )


@router.get("/book/{thread_id}/pdf")
async def get_book_pdf(thread_id: str):
    """Returns the final book as a downloadable PDF."""
    graph = get_graph()
    snapshot = graph.get_state(_get_thread_config(thread_id))

    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")

    state: GraphState = snapshot.values

    if state.get("status") != "done":
        raise HTTPException(status_code=202, detail="Book not ready yet")

    from graph.pdf import markdown_to_pdf
    outline = state.get("book_outline") or {}
    title = outline.get("title", "Tu Libro de Biohacking")
    pdf_bytes = markdown_to_pdf(state.get("final_book", ""), title)

    safe_filename = title[:50].replace(" ", "_").replace("/", "-") + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )
