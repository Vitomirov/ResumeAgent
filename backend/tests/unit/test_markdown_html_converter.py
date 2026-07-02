from app.adapters.pdf.markdown_html_converter import MarkdownHtmlConverter

SAMPLE_MARKDOWN = """# Jane Doe

## Experience

- Built Python APIs with FastAPI
"""


def test_markdown_html_converter_wraps_content() -> None:
    converter = MarkdownHtmlConverter()
    html = converter.convert(SAMPLE_MARKDOWN)

    assert "<!DOCTYPE html>" in html
    assert '<main class="resume">' in html
    assert "<h1>Jane Doe</h1>" in html
    assert "Built Python APIs with FastAPI" in html
    assert "font-family:" in html
