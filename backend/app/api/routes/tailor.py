from fastapi import APIRouter, Depends

from app.api.schemas.common import TailorRequest, TailorResponse
from app.core.dependencies import get_tailor_service
from app.services.tailor_service import TailorService

router = APIRouter()


@router.post("", response_model=TailorResponse)
async def tailor_resume(
    body: TailorRequest,
    service: TailorService = Depends(get_tailor_service),
) -> TailorResponse:
    result = await service.tailor(body.job_description)
    return TailorResponse(
        run_id=result["run_id"],
        markdown=result["markdown"],
        ats_score=result["ats_score"],
    )
