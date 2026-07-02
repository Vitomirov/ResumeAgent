from pathlib import Path

import pytest

from app.core.config import settings
from app.core.errors import ValidationError
from app.services.prompt_repository import PromptRepository


@pytest.fixture
def prompts_dir(tmp_path: Path) -> Path:
    prompt_file = tmp_path / "sample.md"
    prompt_file.write_text(
        """---
system: |
  You are a test assistant.
---

Hello {name}
""",
        encoding="utf-8",
    )
    return tmp_path


def test_load_prompt_from_markdown(prompts_dir: Path) -> None:
    repository = PromptRepository(prompts_dir)

    template = repository.load("sample")

    assert template.system == "You are a test assistant."
    assert template.user == "Hello {name}"


def test_render_substitutes_variables(prompts_dir: Path) -> None:
    repository = PromptRepository(prompts_dir)

    system, user = repository.render("sample", name="World")

    assert system == "You are a test assistant."
    assert user == "Hello World"


def test_render_raises_for_missing_variable(prompts_dir: Path) -> None:
    repository = PromptRepository(prompts_dir)

    with pytest.raises(ValidationError, match="missing variable"):
        repository.render("sample")


def test_load_reloads_when_file_changes(prompts_dir: Path) -> None:
    repository = PromptRepository(prompts_dir)
    original = repository.load("sample")

    prompt_file = prompts_dir / "sample.md"
    prompt_file.write_text(
        """---
system: |
  Updated system prompt.
---

Updated body {name}
""",
        encoding="utf-8",
    )

    updated = repository.load("sample")

    assert original.system != updated.system
    assert updated.system == "Updated system prompt."


def test_all_pipeline_prompts_exist() -> None:
    repository = PromptRepository(settings.prompts_dir)
    expected = [
        "analyze_job",
        "extract_requirements",
        "extract_soft_skills",
        "match_resume",
        "rewrite_resume",
        "generate_resume",
    ]

    for name in expected:
        template = repository.load(name)
        assert template.system
        assert template.user
