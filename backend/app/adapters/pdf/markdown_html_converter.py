from pathlib import Path

import markdown

_CSS_PATH = Path(__file__).resolve().parent / "resume.css"


class MarkdownHtmlConverter:
    """Converts resume markdown into styled HTML ready for PDF rendering."""

    def __init__(self, css_path: Path | None = None) -> None:
        self._css_path = css_path or _CSS_PATH

    def convert(self, markdown_text: str) -> str:
        body = markdown.markdown(
            markdown_text,
            extensions=["extra", "nl2br", "sane_lists"],
        )
        css = self._css_path.read_text(encoding="utf-8")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Resume</title>
  <style>{css}</style>
</head>
<body>
  <main class="resume">{body}</main>
</body>
</html>"""
