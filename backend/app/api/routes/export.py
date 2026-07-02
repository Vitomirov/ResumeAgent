from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.schemas.common import ExportRequest, ExportResponse
from app.core.dependencies import get_export_service
from app.services.export_service import ExportService

router = APIRouter()


@router.post("", response_model=ExportResponse)
async def export_pdf(
    body: ExportRequest,
    service: ExportService = Depends(get_export_service),
) -> ExportResponse:
    result = service.export_pdf(body.run_id)
    return ExportResponse(run_id=result["run_id"], pdf_path=result["pdf_path"])


@router.get("/{run_id}/download")
async def download_pdf(
    run_id: str,
    service: ExportService = Depends(get_export_service),
) -> Response:
    pdf_bytes, filename = service.read_pdf(run_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
