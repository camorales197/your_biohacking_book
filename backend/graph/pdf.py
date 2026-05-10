import markdown as md_lib
from weasyprint import HTML

_CSS = """
@page {
    margin: 2.5cm 2cm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 10px;
        color: #888;
    }
}

body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 1.7;
    color: #1a1a1a;
}

h1 {
    font-size: 26pt;
    color: #14532d;
    border-bottom: 3px solid #14532d;
    padding-bottom: 8px;
    margin-top: 0;
    page-break-after: avoid;
}

h2 {
    font-size: 18pt;
    color: #166534;
    border-bottom: 1px solid #bbf7d0;
    padding-bottom: 4px;
    margin-top: 2em;
    page-break-after: avoid;
}

h3 {
    font-size: 14pt;
    color: #15803d;
    margin-top: 1.5em;
    page-break-after: avoid;
}

h4 {
    font-size: 12pt;
    color: #16a34a;
    margin-top: 1.2em;
    page-break-after: avoid;
}

p {
    margin: 0.6em 0;
    text-align: justify;
}

ul, ol {
    margin: 0.5em 0;
    padding-left: 1.5em;
}

li {
    margin: 0.3em 0;
}

strong {
    color: #14532d;
}

em {
    color: #374151;
}

hr {
    border: none;
    border-top: 1px solid #d1fae5;
    margin: 1.5em 0;
}

blockquote {
    border-left: 4px solid #16a34a;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f0fdf4;
    color: #374151;
}
"""


def markdown_to_pdf(markdown_content: str, title: str) -> bytes:
    """Convert a Markdown string to PDF bytes using WeasyPrint."""
    converter = md_lib.Markdown(extensions=["tables", "fenced_code", "toc", "nl2br"])
    body_html = converter.convert(markdown_content)

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>{_CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

    return HTML(string=full_html).write_pdf()
