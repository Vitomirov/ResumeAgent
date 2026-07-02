import json

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.errors import ValidationError
from app.domain.matching.models import RankedSection, ResumeMatchResult
from app.domain.matching.policies import parse_json_response, validate_match_result

MASTER_RESUME = """# Jane Doe

## Experience

- Built Python APIs with FastAPI at Acme Corp
- Led a team of 4 engineers

## Skills

- Python, FastAPI, PostgreSQL

## Education

- B.S. Computer Science, State University
"""

JOB_DESCRIPTION = "Looking for a Python backend engineer with FastAPI experience."


def _sample_result(**overrides: object) -> ResumeMatchResult:
    section = RankedSection(
        section_id="experience-acme",
        section_title="Experience",
        content="- Built Python APIs with FastAPI at Acme Corp",
        relevance_score=0.95,
        matched_keywords=["Python", "FastAPI"],
        rationale="Direct backend stack overlap",
    )
    defaults = {
        "sections": [section],
        "total_sections_in_resume": 3,
        "matched_section_count": 1,
        "matching_notes": "Prioritized backend experience",
    }
    defaults.update(overrides)
    return ResumeMatchResult(**defaults)


def test_parse_json_response_strips_markdown_fence() -> None:
    payload = {"sections": [], "total_sections_in_resume": 0, "matched_section_count": 0}
    raw = f"```json\n{json.dumps(payload)}\n```"

    parsed = parse_json_response(raw)

    assert parsed == payload


def test_parse_json_response_rejects_invalid_json() -> None:
    with pytest.raises(ValidationError, match="invalid JSON"):
        parse_json_response("not json")


def test_result_sorts_sections_by_relevance() -> None:
    low = RankedSection(
        section_id="education",
        section_title="Education",
        content="- B.S. Computer Science, State University",
        relevance_score=0.4,
        matched_keywords=["Computer Science"],
        rationale="Supporting credential",
    )
    high = RankedSection(
        section_id="experience",
        section_title="Experience",
        content="- Built Python APIs with FastAPI at Acme Corp",
        relevance_score=0.9,
        matched_keywords=["Python"],
        rationale="Primary match",
    )

    result = ResumeMatchResult(
        sections=[low, high],
        total_sections_in_resume=3,
        matched_section_count=2,
    )

    assert result.sections[0].section_id == "experience"
    assert result.sections[1].section_id == "education"


def test_validate_accepts_verbatim_resume_content() -> None:
    validate_match_result(_sample_result(), MASTER_RESUME, JOB_DESCRIPTION)


def test_validate_rejects_fabricated_content() -> None:
    fabricated = _sample_result(
        sections=[
            RankedSection(
                section_id="fake",
                section_title="Experience",
                content="- Invented Kubernetes platform at Fake Corp",
                relevance_score=0.99,
                matched_keywords=["Kubernetes"],
                rationale="Fabricated",
            )
        ]
    )

    with pytest.raises(ValidationError, match="verbatim"):
        validate_match_result(fabricated, MASTER_RESUME, JOB_DESCRIPTION)


def test_validate_accepts_keyword_from_full_master_resume() -> None:
    master = MASTER_RESUME + "\n## Additional Skills\n\n- REST APIs, Docker\n"
    result = _sample_result(
        sections=[
            RankedSection(
                section_id="experience-acme",
                section_title="Experience",
                content="- Built Python APIs with FastAPI at Acme Corp",
                relevance_score=0.95,
                matched_keywords=["REST APIs"],
                rationale="Backend integration overlap",
            )
        ]
    )

    validate_match_result(result, master, JOB_DESCRIPTION)


def test_validate_accepts_plural_keyword_variants() -> None:
    result = _sample_result(
        sections=[
            RankedSection(
                section_id="skills",
                section_title="Skills",
                content="- Python, FastAPI, PostgreSQL",
                relevance_score=0.9,
                matched_keywords=["REST APIs"],
                rationale="Backend integration skills",
            )
        ]
    )

    validate_match_result(result, MASTER_RESUME, "Experience with REST API design.")


def test_validate_rejects_invented_technology_keyword() -> None:
    invented_keyword = _sample_result(
        sections=[
            RankedSection(
                section_id="experience-acme",
                section_title="Experience",
                content="- Built Python APIs with FastAPI at Acme Corp",
                relevance_score=0.95,
                matched_keywords=["Kubernetes"],
                rationale="Keyword not grounded",
            )
        ]
    )

    with pytest.raises(ValidationError, match="Matched keyword"):
        validate_match_result(invented_keyword, MASTER_RESUME, JOB_DESCRIPTION)


def test_validate_rejects_mismatched_section_count() -> None:
    mismatch = _sample_result(matched_section_count=2)

    with pytest.raises(ValidationError, match="matched_section_count"):
        validate_match_result(mismatch, MASTER_RESUME, JOB_DESCRIPTION)


def test_model_rejects_invalid_relevance_score() -> None:
    with pytest.raises(PydanticValidationError):
        RankedSection(
            section_id="experience",
            section_title="Experience",
            content="- Built Python APIs with FastAPI at Acme Corp",
            relevance_score=1.5,
            matched_keywords=["Python"],
            rationale="Invalid score",
        )
