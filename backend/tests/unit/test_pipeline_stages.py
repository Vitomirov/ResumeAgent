from unittest.mock import AsyncMock

import pytest

from app.core.config import settings
from app.domain.pipeline.models import JobDescriptionAnalysisInput
from app.services.pipeline.stages.job_description_analysis_service import (
    JobDescriptionAnalysisService,
)
from app.services.prompt_repository import PromptRepository


@pytest.mark.asyncio
async def test_job_description_analysis_service() -> None:
    openai = AsyncMock()
    openai.generate = AsyncMock(return_value="## Role Summary\nEngineer")
    prompts = PromptRepository(settings.prompts_dir)

    service = JobDescriptionAnalysisService(openai=openai, prompts=prompts)
    result = await service.execute(
        JobDescriptionAnalysisInput(job_description="Hiring a backend engineer.")
    )

    assert result.analysis == "## Role Summary\nEngineer"
    openai.generate.assert_awaited_once()
    system_prompt, user_prompt = openai.generate.await_args.args
    assert "recruiter" in system_prompt.lower()
    assert "Hiring a backend engineer." in user_prompt
