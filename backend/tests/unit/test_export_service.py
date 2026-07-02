from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.adapters.filesystem_storage import FilesystemStorage
from app.core.errors import NotFoundError
from app.services.export_service import ExportService


def test_export_service_writes_pdf(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    storage.write_text(Path("outputs/run-1/tailored_resume.md"), "# Resume")

    renderer = MagicMock()
    renderer.render = MagicMock(return_value=b"%PDF-1.4 test")

    service = ExportService(storage=storage, pdf_renderer=renderer)
    result = service.export_pdf("run-1")

    assert result["run_id"] == "run-1"
    assert storage.read_bytes(Path("outputs/run-1/tailored_resume.pdf")) == b"%PDF-1.4 test"
    renderer.render.assert_called_once_with("# Resume")


def test_export_service_raises_when_markdown_missing(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    service = ExportService(storage=storage, pdf_renderer=MagicMock())

    with pytest.raises(NotFoundError):
        service.export_pdf("missing-run")


def test_read_pdf_generates_when_missing(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    storage.write_text(Path("outputs/run-2/tailored_resume.md"), "# Resume")

    renderer = MagicMock()
    renderer.render = MagicMock(return_value=b"%PDF-1.4 generated")

    service = ExportService(storage=storage, pdf_renderer=renderer)
    pdf_bytes, filename = service.read_pdf("run-2")

    assert pdf_bytes == b"%PDF-1.4 generated"
    assert filename == "resume-run-2.pdf"
