import pytest

from app.core.errors import ValidationError
from app.domain.generation.policies import (
    finalize_generated_resume,
    parse_rewritten_content,
    sanitize_markdown_output,
    validate_generated_resume,
)
from app.domain.generation.resume_sections import (
    apply_profile_header,
    extract_master_section,
    extract_profile_header,
)

MASTER = """# Jane Doe

Chicago | jane@example.com

## Professional Background

- Analyst at Acme

## Education

- BS Computer Science
"""

TEMPLATE = """## Professional Summary

{{ summary }}

## Professional Experience

{{ experience }}

## Skills & Abilities

{{ skills }}

## Professional Background

{{ background }}

## Education

{{ education }}
"""

GENERATED = """# Jane Doe

Chicago | jane@example.com

## Professional Summary

Backend engineer focused on Python and FastAPI.

## Professional Experience

- Built Python APIs with FastAPI at Acme Corp

## Skills & Abilities

**Backend:** Python, FastAPI

## Professional Background

- Analyst at Acme

## Education

- BS Computer Science
"""


def test_extract_profile_header() -> None:
    header = extract_profile_header(MASTER)
    assert header.startswith("# Jane Doe")
    assert "jane@example.com" in header


def test_extract_master_section() -> None:
    education = extract_master_section(MASTER, "Education")
    assert "BS Computer Science" in education


def test_apply_profile_header_replaces_generated_name() -> None:
    body = "## Professional Summary\n\nSummary text"
    merged = apply_profile_header(body, "# Jane Doe\n\nChicago | jane@example.com")
    assert merged.startswith("# Jane Doe")
    assert "## Professional Summary" in merged


def test_finalize_generated_resume_injects_profile() -> None:
    body = "## Professional Summary\n\nSummary"
    merged = finalize_generated_resume(body, MASTER)
    assert '<h1 class="resume-name">Jane Doe</h1>' in merged
    assert "jane@example.com" in merged
    assert "## Professional Summary" in merged


def test_parse_rewritten_content_extracts_sections() -> None:
    text = """## Selected Experience
- Built Python APIs

## Selected Projects
- Internal dashboard

## Selected Skills
- Python, FastAPI
"""

    parsed = parse_rewritten_content(text)

    assert "- Built Python APIs" in parsed.selected_experience
    assert "- Internal dashboard" in parsed.selected_projects
    assert "Python" in parsed.selected_skills


def test_sanitize_markdown_output_strips_fence() -> None:
    raw = "```markdown\n# Resume\n```"

    assert sanitize_markdown_output(raw) == "# Resume"


def test_validate_generated_resume_accepts_valid_output() -> None:
    validate_generated_resume(
        GENERATED,
        TEMPLATE,
        selected_experience="- Built Python APIs with FastAPI at Acme Corp",
        selected_projects="",
        selected_skills="**Backend:** Python, FastAPI",
    )


def test_validate_generated_resume_accepts_paraphrased_content() -> None:
    paraphrased = GENERATED.replace(
        "- Built Python APIs with FastAPI at Acme Corp",
        "- Delivered backend services using Python and FastAPI for Acme Corp",
    )

    validate_generated_resume(
        paraphrased,
        TEMPLATE,
        selected_experience="- Built Python APIs with FastAPI at Acme Corp",
        selected_projects="- Internal dashboard for Acme analytics",
        selected_skills="**Backend:** Python, FastAPI",
    )


def test_validate_generated_resume_rejects_unrelated_output() -> None:
    invalid = """# Jane Doe

Chicago | jane@example.com

## Professional Summary

Mainframe operator.

## Professional Experience

- Maintained COBOL batch jobs

## Skills & Abilities

**Backend:** COBOL, JCL

## Professional Background

- Data entry clerk

## Education

- High school diploma
"""

    with pytest.raises(ValidationError, match="truthful selected content"):
        validate_generated_resume(
            invalid,
            TEMPLATE,
            selected_experience="- Built Python APIs with FastAPI at Acme Corp",
            selected_projects="",
            selected_skills="**Backend:** Python, FastAPI",
        )


def test_validate_generated_resume_rejects_unfilled_placeholders() -> None:
    invalid = GENERATED.replace("Jane Doe", "{{ name }}")

    with pytest.raises(ValidationError, match="unfilled placeholders"):
        validate_generated_resume(
            invalid,
            TEMPLATE,
            selected_experience="- Built Python APIs with FastAPI at Acme Corp",
            selected_projects="",
            selected_skills="**Backend:** Python, FastAPI",
        )


def test_validate_generated_resume_rejects_generic_placeholders() -> None:
    invalid = GENERATED.replace("Jane Doe", "[Your Name]")

    with pytest.raises(ValidationError, match="generic placeholders"):
        validate_generated_resume(
            invalid,
            TEMPLATE,
            selected_experience="- Built Python APIs with FastAPI at Acme Corp",
            selected_projects="",
            selected_skills="**Backend:** Python, FastAPI",
        )


def test_validate_generated_resume_rejects_missing_heading() -> None:
    invalid = GENERATED.replace("## Skills & Abilities\n\n**Backend:** Python, FastAPI", "")

    with pytest.raises(ValidationError, match="missing template heading"):
        validate_generated_resume(
            invalid,
            TEMPLATE,
            selected_experience="- Built Python APIs with FastAPI at Acme Corp",
            selected_projects="",
            selected_skills="**Backend:** Python, FastAPI",
        )
