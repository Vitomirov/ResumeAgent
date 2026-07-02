from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.matching.models import RankedSection, ResumeMatchResult
from app.domain.pipeline.models import (
    ContentRewriteOutput,
    JobDescriptionAnalysisOutput,
    PipelineInput,
    ResumeGenerationOutput,
    SectionMatchingOutput,
    SoftSkillsOutput,
    TechnicalRequirementsOutput,
)
from app.services.pipeline.coordinator import PipelineCoordinator


@pytest.fixture
def pipeline() -> PipelineCoordinator:
    job_analysis = MagicMock()
    job_analysis.execute = AsyncMock(
        return_value=JobDescriptionAnalysisOutput(analysis="analysis result")
    )

    technical = MagicMock()
    technical.execute = AsyncMock(
        return_value=TechnicalRequirementsOutput(requirements="tech requirements")
    )

    soft_skills = MagicMock()
    soft_skills.execute = AsyncMock(return_value=SoftSkillsOutput(soft_skills="soft skills"))

    matching = MagicMock()
    match_result = ResumeMatchResult(
        sections=[
            RankedSection(
                section_id="experience",
                section_title="Experience",
                content="- Built APIs",
                relevance_score=0.9,
                matched_keywords=["APIs"],
                rationale="Relevant",
            )
        ],
        total_sections_in_resume=1,
        matched_section_count=1,
    )
    matching.execute = AsyncMock(
        return_value=SectionMatchingOutput(
            match_result=match_result,
            matched_sections="matched sections",
        )
    )

    rewrite = MagicMock()
    rewrite.execute = AsyncMock(
        return_value=ContentRewriteOutput(
            selected_experience="- Built Python APIs",
            selected_projects="- Internal tooling project",
            selected_skills="- Python, FastAPI",
        )
    )

    generation = MagicMock()
    generation.execute = AsyncMock(
        return_value=ResumeGenerationOutput(final_resume="# Final Resume")
    )

    return PipelineCoordinator(
        job_description_analysis=job_analysis,
        technical_requirements_extraction=technical,
        soft_skills_extraction=soft_skills,
        section_matching=matching,
        content_rewrite=rewrite,
        resume_generation=generation,
    )


@pytest.mark.asyncio
async def test_coordinator_runs_stages_in_order(pipeline: PipelineCoordinator) -> None:
    result = await pipeline.run(
        PipelineInput(
            job_description="We need a Python engineer.",
            master_resume="# Master",
            resume_template="# {{ summary }}",
        )
    )

    assert result.final_resume == "# Final Resume"

    job_analysis = pipeline._job_description_analysis
    technical = pipeline._technical_requirements_extraction
    soft_skills = pipeline._soft_skills_extraction
    matching = pipeline._section_matching
    rewrite = pipeline._content_rewrite
    generation = pipeline._resume_generation

    job_analysis.execute.assert_awaited_once()
    technical.execute.assert_awaited_once()
    soft_skills.execute.assert_awaited_once()
    matching.execute.assert_awaited_once()
    rewrite.execute.assert_awaited_once()
    generation.execute.assert_awaited_once()

    assert job_analysis.execute.await_args.args[0].job_description == "We need a Python engineer."
    assert technical.execute.await_args.args[0].job_analysis == "analysis result"
    assert soft_skills.execute.await_args.args[0].job_analysis == "analysis result"
    assert matching.execute.await_args.args[0].master_resume == "# Master"
    assert rewrite.execute.await_args.args[0].matched_sections == "matched sections"
    assert generation.execute.await_args.args[0].resume_template == "# {{ summary }}"
