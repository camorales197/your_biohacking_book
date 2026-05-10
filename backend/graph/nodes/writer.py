from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import SubSection, WriterInput

WRITER_SYSTEM_PROMPT = """You are an expert biohacking writer. Write clear, science-backed, actionable content
in Spanish for a personalized biohacking book.

Writing style:
- Direct and motivating, like a knowledgeable friend
- Always cite the mechanism (why it works), not just what to do
- Use concrete numbers when available (e.g., "20 minutes of sunlight before 10am")
- Adapt difficulty to the biohacking level (Level 1 = simple habits; Level 5 = precise fine-tuning)
- Length: 200-400 words per subsection

Focus types:
- "Acciones concretas": A numbered list of specific, immediately actionable steps
- "Ciencia detrás del hábito": Explain the biological/physiological mechanism in accessible language
- "Protocolo de implementación": A structured weekly/daily protocol with clear timing"""

WRITER_USER_PROMPT = """Write the following subsection of a personalized biohacking book:

Chapter: {chapter} (Level {level})
Section: {section}
Subsection title: {title}
Focus: {focus}

User profile:
- Age: {age}, Sex: {sex}, Location: {location}
- Health issues: {health_issues}
- Goals: {goals}
- Lifestyle: {lifestyle}

Write the content for this subsection. Start directly with the content (no title heading needed).
Language: Spanish."""


def writer_node(state: WriterInput) -> dict:
    """Writer agent: generates content for a single subsection. Called in parallel via Send()."""
    from graph.llm import get_writer_llm

    section = state["section"]
    profile = state["user_profile"]

    prompt = WRITER_USER_PROMPT.format(
        chapter=section["chapter"],
        level=section["level"],
        section=section["section"],
        title=section["title"],
        focus=section["focus"],
        age=profile["age"],
        sex=profile["sex"],
        location=profile["location"],
        health_issues=", ".join(profile["health_issues"]),
        goals=", ".join(profile["goals"]),
        lifestyle=profile["lifestyle"],
    )

    llm = get_writer_llm()
    messages = [SystemMessage(content=WRITER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    completed_section: SubSection = {**section, "content": response.content.strip()}

    # Returns list because Annotated[list, operator.add] reducer expects list
    return {"written_sections": [completed_section]}
