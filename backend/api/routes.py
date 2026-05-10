import asyncio
import json
import logging
import os
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Query, BackgroundTasks, Request
from fastapi.responses import FileResponse, Response
from langgraph.types import Command
from pydantic import BaseModel, EmailStr
from sse_starlette.sse import EventSourceResponse

from graph.state import UserProfile, GraphState
from graph.graph import get_graph

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


# ── Schemas ───────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    email: EmailStr
    age: int
    sex: str
    location: str
    health_issues: list[str]
    lifestyle: str
    goals: list[str]
    other_info: str = ""
    sleep_hours: float = 7.0
    exercise_frequency: str = "no especificado"
    diet_type: str = "omnívoro"
    stress_level: str = "moderado"
    energy_level: str = "moderado"


class GenerateResponse(BaseModel):
    thread_id: str
    session_token: str
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

def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _verify_token(thread_id: str, token: str) -> GraphState:
    """Fetch state and verify the session token. Raises 401/404 on failure."""
    graph = get_graph()
    snapshot = graph.get_state(_config(thread_id))
    if not snapshot or not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    state: GraphState = snapshot.values
    if state.get("session_token") != token:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return state


async def _run_graph_background(thread_id: str, resume_value: dict) -> None:
    """Background task: resume graph after user approval."""
    try:
        graph = get_graph()
        await graph.ainvoke(Command(resume=resume_value), config=_config(thread_id))
    except Exception:
        logger.exception("Background graph execution failed for thread %s", thread_id)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate_book(req: GenerateRequest):
    """Start a new book generation run. Returns thread_id + session_token."""
    thread_id = str(uuid.uuid4())
    session_token = str(uuid.uuid4())

    profile = UserProfile(
        age=req.age,
        sex=req.sex,
        location=req.location,
        health_issues=req.health_issues,
        lifestyle=req.lifestyle,
        goals=req.goals,
        other_info=req.other_info,
        sleep_hours=req.sleep_hours,
        exercise_frequency=req.exercise_frequency,
        diet_type=req.diet_type,
        stress_level=req.stress_level,
        energy_level=req.energy_level,
    )

    initial_state = GraphState(
        session_token=session_token,
        user_email=str(req.email),
        user_profile=profile,
        book_outline=None,
        sections_to_write=[],
        written_sections=[],
        final_book=None,
        pdf_path=None,
        user_feedback=None,
        status="outlining",
        email_sent=False,
    )

    graph = get_graph()
    await graph.ainvoke(initial_state, config=_config(thread_id))

    return GenerateResponse(thread_id=thread_id, session_token=session_token, status="awaiting_approval")


@router.get("/status/{thread_id}", response_model=StatusResponse)
async def get_status(thread_id: str, x_session_token: str = Header(...)):
    state = _verify_token(thread_id, x_session_token)
    return StatusResponse(
        status=state.get("status", "unknown"),
        outline=state.get("book_outline"),
        sections_count=len(state.get("sections_to_write", [])),
        written_count=len(state.get("written_sections", [])),
        email_sent=state.get("email_sent"),
    )


@router.post("/approve/{thread_id}", response_model=GenerateResponse)
async def approve_outline(
    thread_id: str,
    req: ApproveRequest,
    background_tasks: BackgroundTasks,
    x_session_token: str = Header(...),
):
    """Resume graph. Approvals run in background and return immediately; rejections wait for new outline."""
    state = _verify_token(thread_id, x_session_token)
    resume_value = {"approved": req.approved, "feedback": req.feedback or ""}

    if req.approved:
        # Fire and forget — frontend switches to SSE for real-time progress
        background_tasks.add_task(_run_graph_background, thread_id, resume_value)
        return GenerateResponse(
            thread_id=thread_id,
            session_token=state["session_token"],
            status="writing",
        )
    else:
        # Rejection re-runs architect synchronously (fast) then pauses at interrupt again
        graph = get_graph()
        await graph.ainvoke(Command(resume=resume_value), config=_config(thread_id))
        new_state: GraphState = graph.get_state(_config(thread_id)).values
        return GenerateResponse(
            thread_id=thread_id,
            session_token=state["session_token"],
            status=new_state.get("status", "unknown"),
        )


@router.get("/stream/{thread_id}")
async def stream_progress(
    thread_id: str,
    request: Request,
    x_session_token: Optional[str] = Header(None),
    x_session_token_q: Optional[str] = Query(None, alias="x_session_token"),
):
    """SSE endpoint: streams writing progress events until status=done."""
    token = x_session_token or x_session_token_q
    if not token:
        raise HTTPException(status_code=401, detail="Missing session token")
    _verify_token(thread_id, token)

    async def generator():
        last_written = -1
        deadline = 600  # 10 min max

        for _ in range(deadline):
            if await request.is_disconnected():
                break

            snapshot = get_graph().get_state(_config(thread_id))
            if not snapshot or not snapshot.values:
                break

            state: GraphState = snapshot.values
            written = len(state.get("written_sections", []))
            total = len(state.get("sections_to_write", []))
            status = state.get("status", "unknown")

            if written != last_written or status == "done":
                last_written = written
                yield {
                    "data": json.dumps({
                        "status": status,
                        "written_count": written,
                        "total_count": total,
                    })
                }

            if status == "done":
                break

            await asyncio.sleep(1)

    return EventSourceResponse(generator())


@router.get("/book/{thread_id}", response_model=BookResponse)
async def get_book(thread_id: str, x_session_token: str = Header(...)):
    state = _verify_token(thread_id, x_session_token)
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
async def get_book_pdf(
    thread_id: str,
    x_session_token: Optional[str] = Header(None),
    x_session_token_q: Optional[str] = Query(None, alias="x_session_token"),
):
    """Returns the cached PDF from disk, or regenerates it on demand."""
    token = x_session_token or x_session_token_q
    if not token:
        raise HTTPException(status_code=401, detail="Missing session token")
    state = _verify_token(thread_id, token)
    if state.get("status") != "done":
        raise HTTPException(status_code=202, detail="Book not ready yet")

    outline = state.get("book_outline") or {}
    title = outline.get("title", "Tu Libro de Biohacking")
    safe_name = title[:50].replace(" ", "_").replace("/", "-") + ".pdf"

    # Serve cached PDF if available
    pdf_path = state.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=safe_name)

    # Regenerate on demand (pdf_path missing or file deleted)
    from graph.pdf import markdown_to_pdf
    pdf_bytes = markdown_to_pdf(state.get("final_book", ""), title)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
