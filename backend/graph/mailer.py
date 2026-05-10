import base64
import os
import logging

logger = logging.getLogger(__name__)


def send_book_email(to_email: str, title: str, md_content: str, pdf_bytes: bytes) -> bool:
    """Send the generated book to the user's email with PDF and Markdown attachments.

    Returns True on success, False on failure (non-fatal — book is still available via API).
    """
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key or api_key == "mock":
        logger.info("RESEND_API_KEY not set — skipping email send (mock mode)")
        return False

    try:
        import resend
        resend.api_key = api_key

        from_addr = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
        safe_title = title[:60] + "..." if len(title) > 60 else title

        html_body = f"""
<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #1a1a1a;">
  <h1 style="color: #14532d; border-bottom: 3px solid #14532d; padding-bottom: 8px;">
    📗 Tu Libro de Biohacking
  </h1>
  <p style="font-size: 16px; line-height: 1.6;">
    ¡Hola! Tu libro de biohacking personalizado está listo.
  </p>
  <p style="font-size: 16px; line-height: 1.6;">
    <strong>"{safe_title}"</strong> está adjunto a este correo en dos formatos:
  </p>
  <ul style="font-size: 15px; line-height: 1.8;">
    <li>📄 <strong>PDF</strong> — para leer en cualquier dispositivo y imprimir</li>
    <li>📝 <strong>Markdown</strong> — para editar o importar a Notion/Obsidian</li>
  </ul>
  <p style="font-size: 14px; color: #6b7280; margin-top: 24px; border-top: 1px solid #e5e7eb; padding-top: 16px;">
    Generado con IA multiagente · Biohacking Book Generator
  </p>
</div>
"""

        resend.Emails.send({
            "from": from_addr,
            "to": [to_email],
            "subject": f"📗 Tu libro de biohacking: {safe_title}",
            "html": html_body,
            "attachments": [
                {
                    "filename": "libro_biohacking.pdf",
                    "content": base64.b64encode(pdf_bytes).decode(),
                },
                {
                    "filename": "libro_biohacking.md",
                    "content": base64.b64encode(md_content.encode("utf-8")).decode(),
                },
            ],
        })
        logger.info("Book email sent to %s", to_email)
        return True

    except Exception:
        logger.exception("Failed to send book email to %s", to_email)
        return False
