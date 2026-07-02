from app.core.paths import OUTPUTS_DIR, TAILORED_MARKDOWN, TAILORED_PDF
from app.domain.errors import NotFoundError
from app.ports.pdf_renderer_port import PDFRendererPort
from app.ports.storage_port import StoragePort


class ExportService:
    def __init__(self, storage: StoragePort, pdf_renderer: PDFRendererPort) -> None:
        self._storage = storage
        self._pdf_renderer = pdf_renderer

    def export_pdf(self, run_id: str) -> dict[str, str]:
        markdown = self._read_markdown(run_id)
        pdf_bytes = self._pdf_renderer.render(markdown)
        pdf_path = OUTPUTS_DIR / run_id / TAILORED_PDF
        self._storage.write_bytes(pdf_path, pdf_bytes)
        return {"run_id": run_id, "pdf_path": str(pdf_path)}

    def read_pdf(self, run_id: str) -> tuple[bytes, str]:
        pdf_path = OUTPUTS_DIR / run_id / TAILORED_PDF
        if not self._storage.exists(pdf_path):
            self.export_pdf(run_id)
        return self._storage.read_bytes(pdf_path), f"resume-{run_id}.pdf"

    def _read_markdown(self, run_id: str) -> str:
        markdown_path = OUTPUTS_DIR / run_id / TAILORED_MARKDOWN
        if not self._storage.exists(markdown_path):
            raise NotFoundError(f"Tailored resume not found for run_id: {run_id}")
        return self._storage.read_text(markdown_path)
