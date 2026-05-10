import logging
import os

from graph.state import GraphState, SubSection

logger = logging.getLogger(__name__)


def assembler_node(state: GraphState) -> dict:
    """Assembles written sections into Markdown, generates PDF (cached to disk), and emails the book."""
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

    # Generate PDF and cache to disk
    pdf_path: str | None = None
    thread_id = state.get("session_token", "unknown")

    try:
        from graph.pdf import markdown_to_pdf
        pdf_bytes = markdown_to_pdf(final_book, outline["title"])
        pdf_dir = os.getenv("PDF_DIR", "./pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{thread_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception:
        logger.exception("PDF generation failed — book still available as Markdown")
        pdf_bytes = None

    # Send email (non-fatal)
    email_sent = False
    user_email = state.get("user_email", "")
    if user_email and pdf_bytes is not None:
        try:
            from graph.mailer import send_book_email
            email_sent = send_book_email(user_email, outline["title"], final_book, pdf_bytes)
        except Exception:
            logger.exception("Email delivery failed")

    return {
        "final_book": final_book,
        "pdf_path": pdf_path,
        "status": "done",
        "email_sent": email_sent,
    }
