import time
from pathlib import Path

import pytest

from app.adapters.filesystem_storage import FilesystemStorage
from app.core.errors import NotFoundError
from app.services.preview_service import PreviewService


def test_preview_service_get_by_run_id(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    storage.write_text(Path("outputs/abc/tailored_resume.md"), "# Tailored")

    service = PreviewService(storage=storage)
    result = service.get_by_run_id("abc")

    assert result["run_id"] == "abc"
    assert result["markdown"] == "# Tailored"


def test_preview_service_get_latest(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    storage.write_text(Path("outputs/old/tailored_resume.md"), "# Old")
    time.sleep(0.01)
    storage.write_text(Path("outputs/new/tailored_resume.md"), "# New")

    service = PreviewService(storage=storage)
    result = service.get_latest()

    assert result["run_id"] == "new"


def test_preview_service_raises_when_empty(tmp_path: Path) -> None:
    service = PreviewService(storage=FilesystemStorage(tmp_path))

    with pytest.raises(NotFoundError):
        service.get_latest()
