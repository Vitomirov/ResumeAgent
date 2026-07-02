import json
from unittest.mock import AsyncMock

import pytest

from app.domain.matching.models import RankedSection, ResumeMatchResult
from app.domain.pipeline.models import SectionMatchingInput
from app.services.matching.resume_matching_engine import ResumeMatchingEngine
from app.services.pipeline.stages.section_matching_service import SectionMatchingService


@pytest.mark.asyncio
async def test_section_matching_service_delegates_to_engine() -> None:
    match_result = ResumeMatchResult(
        sections=[
            RankedSection(
                section_id="skills",
                section_title="Skills",
                content="- Python, FastAPI, PostgreSQL",
                relevance_score=0.88,
                matched_keywords=["Python", "FastAPI"],
                rationale="Stack overlap",
            )
        ],
        total_sections_in_resume=2,
        matched_section_count=1,
        matching_notes="Focused on backend skills",
    )
    engine = AsyncMock(spec=ResumeMatchingEngine)
    engine.match = AsyncMock(return_value=match_result)

    service = SectionMatchingService(matching_engine=engine)
    output = await service.execute(
        SectionMatchingInput(
            master_resume="## Skills\n- Python, FastAPI, PostgreSQL",
            job_description="Python backend role",
        )
    )

    engine.match.assert_awaited_once_with(
        master_resume="## Skills\n- Python, FastAPI, PostgreSQL",
        job_description="Python backend role",
    )
    assert output.match_result == match_result
    assert json.loads(output.matched_sections)["sections"][0]["section_id"] == "skills"
