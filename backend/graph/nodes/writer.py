from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import SubSection, WriterInput

WRITER_SYSTEM_PROMPT = """You are a world-class biohacking writer and health science communicator.
Write engaging, rigorous, personalized content in **Spanish** for a biohacking book.

## Writing rules
- Voice: knowledgeable friend, not a textbook — warm, direct, motivating
- Every claim needs a mechanism: don't just say "sleep 8 hours", explain WHY (adenosine clearance, HGH release, memory consolidation)
- Use concrete specifics: times, doses, durations (e.g., "20min de luz solar antes de las 10am", "400mg magnesio bisglicinato 1h antes de dormir")
- Adapt difficulty strictly to the biohacking level (Level 1 = no friction habits; Level 5 = precise fine-tuning)
- Always personalize to the user's health issues and goals — mention their conditions by name when relevant
- Add 1-2 scientific references in parentheses when possible: (Walker, 2017; Huberman Lab, 2022)
- Length: 250-450 words per subsection

## Focus types
- **"Acciones concretas"**: numbered list of ≥5 immediately doable steps, each specific and measurable
- **"Ciencia detrás del hábito"**: explain the biological/physiological chain of events in plain language; include at least one reference
- **"Protocolo de implementación"**: structured protocol with explicit timing (morning/afternoon/evening), frequency, and duration

## Contraindications
If the user has a relevant health condition AND the section involves a potentially risky protocol
(fasting, cold exposure, sauna, intense exercise, supplements), include a short "⚠️ Precaución" paragraph at the end."""

WRITER_USER_PROMPT = """Write the following subsection for a personalized biohacking book.

**Book:** {book_title}
**Chapter:** {chapter} (Level {level})
**Section:** {section}
**Subsection title:** {title}
**Focus type:** {focus}

**User profile (personalize every sentence to this person):**
- Age: {age} | Sex: {sex} | Location: {location}
- Sleep: {sleep_hours}h/night | Exercise: {exercise_frequency} | Diet: {diet_type}
- Stress: {stress_level} | Energy: {energy_level}
- Health issues: {health_issues}
- Goals: {goals}

**Sections already covered in this chapter (avoid repetition):**
{covered_sections}

Write the subsection content now. Start directly — no heading, no preamble. Language: Spanish."""


def writer_node(state: WriterInput) -> dict:
    """Writes one subsection. Receives full outline context to avoid repetition."""
    from graph.llm import get_writer_llm

    section = state["section"]
    profile = state["user_profile"]
    outline = state.get("book_outline", {})

    # Build list of sibling sections already in the same chapter
    covered: list[str] = []
    for ch in outline.get("chapters", []):
        if ch["title"] == section["chapter"]:
            for s in ch.get("sections", []):
                if s["title"] != section["section"]:
                    covered.append(f"- {s['title']}")
            break
    covered_text = "\n".join(covered) if covered else "(primera sección del capítulo)"

    prompt = WRITER_USER_PROMPT.format(
        book_title=outline.get("title", "Tu Libro de Biohacking"),
        chapter=section["chapter"],
        level=section["level"],
        section=section["section"],
        title=section["title"],
        focus=section["focus"],
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
        covered_sections=covered_text,
    )

    llm = get_writer_llm()
    messages = [SystemMessage(content=WRITER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    completed_section: SubSection = {**section, "content": response.content.strip()}
    return {"written_sections": [completed_section]}
