from graph.state import GraphState, SubSection


def assembler_node(state: GraphState) -> dict:
    """Assembles written sections into Markdown, generates PDF, and emails the book."""
    written: list[SubSection] = state["written_sections"]
    outline = state["book_outline"]

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

    # Generate PDF and send email (both non-fatal on failure)
    email_sent = False
    user_email = state.get("user_email", "")

    if user_email:
        from graph.pdf import markdown_to_pdf
        from graph.mailer import send_book_email
        try:
            pdf_bytes = markdown_to_pdf(final_book, outline["title"])
            email_sent = send_book_email(user_email, outline["title"], final_book, pdf_bytes)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("PDF/email step failed: %s", exc)

    return {
        "final_book": final_book,
        "status": "done",
        "email_sent": email_sent,
    }
