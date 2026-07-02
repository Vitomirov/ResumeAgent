from weasyprint import HTML

from app.adapters.pdf.markdown_html_converter import MarkdownHtmlConverter
from app.ports.pdf_renderer_port import PDFRendererPort


class MarkdownPDFRenderer(PDFRendererPort):
    """Renders resume markdown to PDF via HTML (Markdown → HTML → PDF)."""

    def __init__(self, converter: MarkdownHtmlConverter | None = None) -> None:
        self._converter = converter or MarkdownHtmlConverter()

    def render(self, markdown: str) -> bytes:
        html = self._converter.convert(markdown)
        return HTML(string=html).write_pdf()
