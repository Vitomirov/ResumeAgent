from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_export_service
from app.main import app
from app.services.export_service import ExportService


@pytest.mark.asyncio
async def test_download_pdf_endpoint() -> None:
    export_service = MagicMock(spec=ExportService)
    export_service.read_pdf = MagicMock(return_value=(b"%PDF-1.4 test", "resume-test.pdf"))

    app.dependency_overrides[get_export_service] = lambda: export_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/export/test/download")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content == b"%PDF-1.4 test"
