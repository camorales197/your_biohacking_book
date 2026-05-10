from graph.state import GraphState, SubSection


def assembler_node(state: GraphState) -> dict:
    """Assembles all written sections into a single formatted Markdown document."""
    written: list[SubSection] = state["written_sections"]
    outline = state["book_outline"]

    # Sort by chapter_index then section_index then subsection order (id sorts lexicographically)
    written_sorted = sorted(written, key=lambda s: s["id"])

    lines: list[str] = []
    lines.append(f"# {outline['title']}\n")

    current_chapter = None
    current_section = None

    for sub in written_sorted:
        if sub["chapter"] != current_chapter:
            current_chapter = sub["chapter"]
            current_section = None
            lines.append(f"\n## {current_chapter}\n")

        if sub["section"] != current_section:
            current_section = sub["section"]
            lines.append(f"\n### {current_section}\n")

        focus_emoji = {
            "Acciones concretas": "⚡",
            "Ciencia detrás del hábito": "🔬",
            "Protocolo de implementación": "📋",
        }.get(sub["focus"], "📌")

        lines.append(f"\n#### {focus_emoji} {sub['title']}\n")
        if sub.get("content"):
            lines.append(sub["content"])
            lines.append("")

    final_book = "\n".join(lines)

    return {
        "final_book": final_book,
        "status": "done",
    }
