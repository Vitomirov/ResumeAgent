from fastapi import APIRouter, Depends

from app.api.schemas.common import TextContent
from app.core.dependencies import get_input_service
from app.services.input_service import InputService

router = APIRouter()


@router.get("/master", response_model=TextContent)
async def get_master_resume(
    service: InputService = Depends(get_input_service),
) -> TextContent:
    return TextContent(content=service.get_master_resume())


@router.put("/master", response_model=TextContent)
async def save_master_resume(
    body: TextContent,
    service: InputService = Depends(get_input_service),
) -> TextContent:
    service.save_master_resume(body.content)
    return TextContent(content=body.content)


@router.get("/template", response_model=TextContent)
async def get_template(
    service: InputService = Depends(get_input_service),
) -> TextContent:
    return TextContent(content=service.get_template())


@router.put("/template", response_model=TextContent)
async def save_template(
    body: TextContent,
    service: InputService = Depends(get_input_service),
) -> TextContent:
    service.save_template(body.content)
    return TextContent(content=body.content)
