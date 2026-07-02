from unittest.mock import AsyncMock

import pytest

from app.domain.generation.models import ResumeGeneratorInput
from app.services.generation.resume_generator import ResumeGenerator
from app.services.prompt_repository import PromptRepository

MASTER = """# Jane Doe

Chicago | jane@example.com

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

GENERATED = """## Professional Summary

Backend engineer focused on Python and FastAPI.

## Professional Experience

- Built Python APIs with FastAPI at Acme Corp

## Skills & Abilities

**Backend:** Python, FastAPI

## Professional Background

- Prior analyst role

## Education

- BS Computer Science
"""


@pytest.mark.asyncio
async def test_resume_generator_injects_profile_header(tmp_path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "generate_resume.md").write_text(
        """---
system: |
  Generate resume markdown.
---

Template: {resume_template}
Education: {reference_education}
Background: {reference_background}
Experience: {selected_experience}
Projects: {selected_projects}
Skills: {selected_skills}
""",
        encoding="utf-8",
    )

    openai = AsyncMock()
    openai.generate = AsyncMock(return_value=GENERATED)

    generator = ResumeGenerator(
        openai=openai,
        prompts=PromptRepository(prompts_dir),
    )

    result = await generator.generate(
        ResumeGeneratorInput(
            resume_template=TEMPLATE,
            master_resume=MASTER,
            profile_header="# Jane Doe\n\nChicago | jane@example.com",
            reference_education="- BS Computer Science",
            reference_background="- Prior analyst role",
            reference_certifications="",
            selected_experience="- Built Python APIs with FastAPI at Acme Corp",
            selected_projects="",
            selected_skills="**Backend:** Python, FastAPI",
        )
    )

    assert '<h1 class="resume-name">Jane Doe</h1>' in result.markdown
    assert "Chicago" in result.markdown
    assert "jane@example.com" in result.markdown
    assert "## Professional Summary" in result.markdown
    openai.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_resume_generator_rejects_invalid_output(tmp_path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "generate_resume.md").write_text(
        """---
system: |
  Generate resume markdown.
---

Template: {resume_template}
Education: {reference_education}
Background: {reference_background}
Experience: {selected_experience}
Projects: {selected_projects}
Skills: {selected_skills}
""",
        encoding="utf-8",
    )

    openai = AsyncMock()
    openai.generate = AsyncMock(return_value="## Professional Summary\n\n[Your Name]")

    generator = ResumeGenerator(
        openai=openai,
        prompts=PromptRepository(prompts_dir),
    )

    from app.core.errors import ValidationError

    with pytest.raises(ValidationError):
        await generator.generate(
            ResumeGeneratorInput(
                resume_template=TEMPLATE,
                master_resume=MASTER,
                profile_header="# Jane Doe\n\nChicago | jane@example.com",
                reference_education="- BS Computer Science",
                reference_background="",
                reference_certifications="",
                selected_experience="- Built Python APIs with FastAPI at Acme Corp",
                selected_projects="",
                selected_skills="**Backend:** Python, FastAPI",
            )
        )
