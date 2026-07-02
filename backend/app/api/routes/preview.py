from fastapi import APIRouter, Depends

from app.api.schemas.common import PreviewResponse
from app.core.dependencies import get_preview_service
from app.services.preview_service import PreviewService

router = APIRouter()


@router.get("/latest", response_model=PreviewResponse)
async def get_latest_preview(
    service: PreviewService = Depends(get_preview_service),
) -> PreviewResponse:
    result = service.get_latest()
    return PreviewResponse(run_id=result["run_id"], markdown=result["markdown"])


@router.get("/{run_id}", response_model=PreviewResponse)
async def get_preview_by_run_id(
    run_id: str,
    service: PreviewService = Depends(get_preview_service),
) -> PreviewResponse:
    result = service.get_by_run_id(run_id)
    return PreviewResponse(run_id=result["run_id"], markdown=result["markdown"])
