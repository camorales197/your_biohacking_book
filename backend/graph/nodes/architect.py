import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt

from graph.state import GraphState, BookOutline, SubSection
from graph.sanitize import sanitize_profile

ARCHITECT_SYSTEM_PROMPT = """You are a world-class biohacking book architect and health optimization expert.
Your task is to design a deeply personalized, science-backed book structure for a specific user.

## Book structure rules

Chapters: Introducción → Nivel 1 → Nivel 2 → Nivel 3 → Nivel 4 → Nivel 5 → Día Tipo → Conclusión
Sections: 2-3 thematic areas per chapter (Nutrición, Sueño, Movimiento, Mente, etc.)
Subsections: 2-3 per section, each with ONE of these focuses:
  - "Acciones concretas": numbered list of immediately actionable steps
  - "Ciencia detrás del hábito": the biological/physiological mechanism
  - "Protocolo de implementación": a structured daily/weekly protocol with timing

## 5 biohacking levels (progressive)
- Level 1 – Fundamentos: bedrock habits everyone needs first (sleep 8h, 2L water, remove ultra-processed food, 30min daily movement)
- Level 2 – Optimización Básica: sleep quality, meal timing, omega-3, morning sunlight, stress management
- Level 3 – Optimización Intermedia: time-restricted eating, cold exposure, zone-2 cardio, HRV tracking, magnesium/vitamin D
- Level 4 – Biohacking Avanzado: sauna protocols, VO2max training, continuous glucose monitoring, targeted supplementation
- Level 5 – Ajuste Fino: precise micro-optimizations (e.g., eat the whole orange not the juice, leucine timing, nasal breathing during sleep)

## Mandatory personalization rules
Apply these rules based on the user profile:
- Insulin resistance / metabolic issues → glucose management takes priority in L1-L2; CGM appears in L4; no fruit juice anywhere
- Poor sleep (< 7h) → sleep protocol is the FIRST section in L1; blue light, caffeine cutoff, temperature in L2
- High stress → HPA axis, cortisol management sections in L2-L3; adaptogens in L4
- Sedentary lifestyle → movement before any other optimization; start with walking, not HIIT
- Keto/vegan/vegetarian diet → adapt ALL nutrition sections; supplement gaps (B12, iron, omega-3 if vegan)
- Low energy → mitochondrial health thread through L2-L4; CoQ10, sleep architecture, light exposure
- Overweight goals → caloric awareness in L1, metabolic flexibility in L3, NOT calorie counting obsession

## "Día Tipo" chapter (mandatory)
The penultimate chapter must be "Mi Día Tipo Optimizado" (level: 0).
It must contain ONE section "Protocolo Diario" with 3 subsections:
  1. "Mañana: Ritual de Alto Rendimiento" – focus: "Protocolo de implementación"
  2. "Tarde: Nutrición y Movimiento" – focus: "Protocolo de implementación"
  3. "Noche: Recuperación y Sueño" – focus: "Protocolo de implementación"
These must be completely personalized to the user's schedule, conditions, and goals.

## Contraindications
For users with specific health conditions, add a "Precauciones importantes" subsection in any chapter where risky protocols appear.
Focus: "Ciencia detrás del hábito" (explain WHY the caution exists medically).

Output ONLY valid JSON. No markdown fences, no explanation outside the JSON."""


ARCHITECT_USER_PROMPT = """Design the personalized biohacking book for this user:

**Profile:**
- Age: {age} | Sex: {sex} | Location: {location}
- Average sleep: {sleep_hours}h/night
- Exercise: {exercise_frequency}
- Diet: {diet_type}
- Stress level: {stress_level} | Energy level: {energy_level}
- Health issues: {health_issues}
- Goals: {goals}
- Lifestyle: {lifestyle}
- Additional notes: {other_info}

{feedback_section}

**Critical personalization required:** Every chapter title, section name, and subsection title must reflect THIS user's specific conditions and goals — not generic biohacking topics.

Return a JSON object:
{{
  "title": "Tu Libro de Biohacking: [specific subtitle reflecting main goal]",
  "chapters": [
    {{
      "title": "Introducción: Tu Hoja de Ruta Personalizada",
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
    {{ "title": "Nivel 1: Fundamentos", "level": 1, "sections": [...] }},
    {{ "title": "Nivel 2: Optimización Básica", "level": 2, "sections": [...] }},
    {{ "title": "Nivel 3: Optimización Intermedia", "level": 3, "sections": [...] }},
    {{ "title": "Nivel 4: Biohacking Avanzado", "level": 4, "sections": [...] }},
    {{ "title": "Nivel 5: Ajuste Fino", "level": 5, "sections": [...] }},
    {{ "title": "Mi Día Tipo Optimizado", "level": 0, "sections": [...] }},
    {{ "title": "Conclusión: Tu Plan de Acción", "level": 0, "sections": [...] }}
  ]
}}"""


def _flatten_outline(outline: BookOutline) -> list[SubSection]:
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
    """Generates the personalized book outline. Commits to state before HITL pause."""
    from graph.llm import get_architect_llm

    profile = sanitize_profile(dict(state["user_profile"]))
    feedback = state.get("user_feedback") or ""
    feedback_section = (
        f"\n**User feedback on previous outline — revise accordingly:**\n{feedback}"
        if feedback else ""
    )

    prompt = ARCHITECT_USER_PROMPT.format(
        age=profile["age"],
        sex=profile["sex"],
        location=profile["location"],
        sleep_hours=profile.get("sleep_hours", "?"),
        exercise_frequency=profile.get("exercise_frequency", "no especificado"),
        diet_type=profile.get("diet_type", "no especificado"),
        stress_level=profile.get("stress_level", "no especificado"),
        energy_level=profile.get("energy_level", "no especificado"),
        health_issues=", ".join(profile["health_issues"]) or "ninguno",
        goals=", ".join(profile["goals"]),
        lifestyle=profile["lifestyle"],
        other_info=profile["other_info"] or "ninguna",
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

    return {
        "book_outline": outline,
        "sections_to_write": sections_to_write,
        "user_feedback": None,
        "status": "awaiting_approval",
    }


def hitl_node(state: GraphState) -> dict:
    """Pauses for user outline review. Resumes via Command(resume={approved, feedback})."""
    user_decision = interrupt({
        "type": "outline_review",
        "outline": state["book_outline"],
        "sections_count": len(state["sections_to_write"]),
    })

    approved = user_decision.get("approved", False) if isinstance(user_decision, dict) else False
    feedback = user_decision.get("feedback", "") if isinstance(user_decision, dict) else ""

    return {
        "user_feedback": feedback if not approved else None,
        "status": "writing" if approved else "awaiting_approval",
    }
