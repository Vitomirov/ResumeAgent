import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.domain.errors import ValidationError

_FRONTMATTER_PATTERN = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user: str


@dataclass
class _CachedPrompt:
    template: PromptTemplate
    mtime_ns: int


class PromptRepository:
    """Loads and renders AI prompts from markdown files."""

    def __init__(self, prompts_dir: Path) -> None:
        self._prompts_dir = prompts_dir.resolve()
        self._cache: dict[str, _CachedPrompt] = {}

    def load(self, name: str) -> PromptTemplate:
        path = self._prompts_dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")

        mtime_ns = path.stat().st_mtime_ns
        cached = self._cache.get(name)
        if cached is not None and cached.mtime_ns == mtime_ns:
            return cached.template

        template = _parse_prompt_file(path.read_text(encoding="utf-8"), path)
        self._cache[name] = _CachedPrompt(template=template, mtime_ns=mtime_ns)
        return template

    def render(self, prompt_name: str, **variables: str) -> tuple[str, str]:
        template = self.load(prompt_name)
        try:
            user_prompt = template.user.format(**variables)
        except KeyError as exc:
            missing = exc.args[0]
            raise ValidationError(
                f"Prompt '{prompt_name}' is missing variable: {{{missing}}}"
            ) from exc
        return template.system, user_prompt


def _parse_prompt_file(content: str, path: Path) -> PromptTemplate:
    match = _FRONTMATTER_PATTERN.match(content)
    if match is None:
        raise ValidationError(f"Prompt file '{path.name}' must start with YAML frontmatter")

    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ValidationError(f"Prompt file '{path.name}' has invalid frontmatter")

    system = metadata.get("system")
    if not isinstance(system, str) or not system.strip():
        raise ValidationError(f"Prompt file '{path.name}' must define a non-empty 'system' field")

    user = content[match.end() :].strip("\n")
    if not user.strip():
        raise ValidationError(f"Prompt file '{path.name}' must include a user prompt body")

    return PromptTemplate(system=system.strip(), user=user)
