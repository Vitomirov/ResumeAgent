import json
from unittest.mock import AsyncMock

import pytest

from app.domain.matching.models import ResumeMatchResult
from app.services.matching.resume_matching_engine import ResumeMatchingEngine
from app.services.prompt_repository import PromptRepository

MASTER_RESUME = """## Experience
- Built Python APIs with FastAPI at Acme Corp
"""

JOB_DESCRIPTION = "Python backend engineer with FastAPI."


@pytest.fixture
def matching_payload() -> dict:
    return {
        "sections": [
            {
                "section_id": "experience-acme",
                "section_title": "Experience",
                "content": "- Built Python APIs with FastAPI at Acme Corp",
                "relevance_score": 0.93,
                "matched_keywords": ["Python", "FastAPI"],
                "rationale": "Matches core backend requirements",
            }
        ],
        "total_sections_in_resume": 1,
        "matched_section_count": 1,
        "matching_notes": "Selected the only relevant experience section",
    }


@pytest.mark.asyncio
async def test_matching_engine_returns_ranked_json(
    tmp_path,
    matching_payload: dict,
) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "match_resume.md").write_text(
        """---
system: |
  Match resume sections.
---

Resume: {master_resume}
Job: {job_description}
""",
        encoding="utf-8",
    )

    openai = AsyncMock()
    openai.generate = AsyncMock(return_value=json.dumps(matching_payload))

    engine = ResumeMatchingEngine(
        openai=openai,
        prompts=PromptRepository(prompts_dir),
    )

    result = await engine.match(MASTER_RESUME, JOB_DESCRIPTION)

    assert isinstance(result, ResumeMatchResult)
    assert result.sections[0].section_id == "experience-acme"
    assert result.sections[0].relevance_score == 0.93
    openai.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_matching_engine_rejects_fabricated_llm_output(tmp_path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "match_resume.md").write_text(
        """---
system: |
  Match resume sections.
---

Resume: {master_resume}
Job: {job_description}
""",
        encoding="utf-8",
    )

    fabricated_payload = {
        "sections": [
            {
                "section_id": "fake",
                "section_title": "Experience",
                "content": "- Operated fictional Rust microservices",
                "relevance_score": 0.99,
                "matched_keywords": ["Rust"],
                "rationale": "Fabricated",
            }
        ],
        "total_sections_in_resume": 1,
        "matched_section_count": 1,
        "matching_notes": "Bad output",
    }

    openai = AsyncMock()
    openai.generate = AsyncMock(return_value=json.dumps(fabricated_payload))

    engine = ResumeMatchingEngine(
        openai=openai,
        prompts=PromptRepository(prompts_dir),
    )

    from app.core.errors import ValidationError

    with pytest.raises(ValidationError):
        await engine.match(MASTER_RESUME, JOB_DESCRIPTION)
