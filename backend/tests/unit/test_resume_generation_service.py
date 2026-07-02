from unittest.mock import AsyncMock

import pytest

from app.domain.generation.models import ResumeGeneratorOutput
from app.domain.pipeline.models import ResumeGenerationInput
from app.services.generation.resume_generator import ResumeGenerator
from app.services.pipeline.stages.resume_generation_service import ResumeGenerationService


@pytest.mark.asyncio
async def test_resume_generation_service_delegates_to_generator() -> None:
    generator = AsyncMock(spec=ResumeGenerator)
    generator.generate = AsyncMock(
        return_value=ResumeGeneratorOutput(markdown="# Tailored Resume")
    )

    service = ResumeGenerationService(resume_generator=generator)
    result = await service.execute(
        ResumeGenerationInput(
            resume_template="# {{ summary }}",
            master_resume="# Jane Doe\n\njane@example.com",
            profile_header="# Jane Doe\n\njane@example.com",
            reference_education="- BS",
            reference_background="- Analyst",
            reference_certifications="",
            selected_experience="- Built APIs",
            selected_projects="- Side project",
            selected_skills="- Python",
        )
    )

    assert result.final_resume == "# Tailored Resume"
    generator.generate.assert_awaited_once()
