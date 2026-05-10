import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt

from graph.state import GraphState, BookOutline, SubSection

ARCHITECT_SYSTEM_PROMPT = """You are an expert biohacking book architect. Your task is to design a personalized,
science-backed biohacking book structure for a specific user.

The book must follow this 5-level progressive structure:
- Level 1 (Fundamentos): Basic, high-impact habits (hydration, 8h sleep, avoiding ultra-processed foods, daily movement)
- Level 2 (Optimización Básica): First-order optimizations (sleep quality, meal timing, basic supplementation)
- Level 3 (Optimización Intermedia): Deeper interventions (HRV tracking, cold exposure, intermittent fasting)
- Level 4 (Biohacking Avanzado): Advanced protocols (zone 2 training, sauna, specific supplements by biomarkers)
- Level 5 (Ajuste Fino): Precise fine-tuning (e.g., eating the whole orange instead of juice to avoid glucose spikes)

Book structure: Chapters (Intro, Nivel 1-5, Conclusión) → Sections (themes: Nutrición, Sueño, Ejercicio, etc.) →
Subsections with ONE specific focus each:
  - "Acciones concretas": Actionable steps the user can implement today
  - "Ciencia detrás del hábito": The scientific mechanism explained simply
  - "Protocolo de implementación": Step-by-step protocol for this habit

Adapt ALL content to the user's specific profile, health issues, goals, and lifestyle.
Output ONLY valid JSON matching the BookOutline schema. No markdown, no explanation."""

ARCHITECT_USER_PROMPT = """Create a personalized biohacking book outline for this user:

Age: {age}
Sex: {sex}
Location: {location}
Health issues: {health_issues}
Lifestyle: {lifestyle}
Goals: {goals}
Additional info: {other_info}

{feedback_section}

Return a JSON object with this exact structure:
{{
  "title": "Tu Libro de Biohacking Personalizado: [personalized subtitle]",
  "chapters": [
    {{
      "title": "Introducción",
      "level": 0,
      "sections": [
        {{
          "title": "section title",
          "subsections": [
            {{"title": "subsection title", "focus": "Acciones concretas"}}
          ]
        }}
      ]
    }},
    {{
      "title": "Nivel 1: Fundamentos",
      "level": 1,
      "sections": [...]
    }},
    ... (levels 2-5 + Conclusión)
  ]
}}

Generate 2-3 sections per chapter, 2-3 subsections per section. Be specific and personalized."""


def _flatten_outline(outline: BookOutline) -> list[SubSection]:
    """Converts hierarchical outline into flat list of SubSection items for parallel writing."""
    sections: list[SubSection] = []
    for ch_idx, chapter in enumerate(outline["chapters"]):
        for s_idx, section in enumerate(chapter["sections"]):
            for sub_idx, subsection in enumerate(section["subsections"]):
                section_id = f"ch{ch_idx:02d}_s{s_idx:02d}_sub{sub_idx:02d}"
                sections.append(SubSection(
                    id=section_id,
                    chapter=chapter["title"],
                    chapter_index=ch_idx,
                    section=section["title"],
                    section_index=s_idx,
                    title=subsection["title"],
                    focus=subsection["focus"],
                    level=chapter.get("level", 0),
                    content=None,
                ))
    return sections


def architect_node(state: GraphState) -> dict:
    """Architect agent: generates or regenerates the book outline using an LLM.

    Commits outline to state BEFORE the HITL interrupt node runs.
    """
    from graph.llm import get_architect_llm

    profile = state["user_profile"]
    feedback = state.get("user_feedback") or ""
    feedback_section = (
        f"\nUser feedback on previous outline:\n{feedback}\nPlease revise accordingly."
        if feedback else ""
    )

    prompt = ARCHITECT_USER_PROMPT.format(
        age=profile["age"],
        sex=profile["sex"],
        location=profile["location"],
        health_issues=", ".join(profile["health_issues"]),
        lifestyle=profile["lifestyle"],
        goals=", ".join(profile["goals"]),
        other_info=profile["other_info"],
        feedback_section=feedback_section,
    )

    llm = get_architect_llm()
    messages = [SystemMessage(content=ARCHITECT_SYSTEM_PROMPT), HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    outline: BookOutline = json.loads(raw)
    sections_to_write = _flatten_outline(outline)

    # Commit outline and sections to state — HITL interrupt happens in the next node
    return {
        "book_outline": outline,
        "sections_to_write": sections_to_write,
        "user_feedback": None,
        "status": "awaiting_approval",
    }


def hitl_node(state: GraphState) -> dict:
    """Human-in-the-loop node: pauses execution for user outline review.

    The interrupt value is delivered to the frontend. When the user approves or
    provides feedback, the graph resumes here via Command(resume={...}).
    """
    outline = state["book_outline"]
    sections_count = len(state["sections_to_write"])

    user_decision = interrupt({
        "type": "outline_review",
        "outline": outline,
        "sections_count": sections_count,
    })

    approved = user_decision.get("approved", False) if isinstance(user_decision, dict) else False
    feedback = user_decision.get("feedback", "") if isinstance(user_decision, dict) else ""

    return {
        "user_feedback": feedback if not approved else None,
        "status": "writing" if approved else "awaiting_approval",
    }
