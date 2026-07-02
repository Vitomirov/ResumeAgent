import re

from app.domain.errors import ValidationError
from app.domain.generation.models import ParsedRewrittenContent
from app.domain.generation.experience_formatter import format_generated_resume
from app.domain.generation.resume_sections import (
    apply_profile_header,
    extract_profile_header,
    has_unfilled_template_placeholders,
    reject_generic_placeholders,
)

_MARKDOWN_FENCE_PATTERN = re.compile(r"^```(?:markdown)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)
_HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
_TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")
_TECH_SHORT_TOKENS = frozenset(
    {"ai", "api", "aws", "cd", "ci", "css", "git", "go", "js", "jwt", "llm", "sql", "ui", "ux"}
)
_GENERIC_RESUME_TOKENS = frozenset(
    {
        "acme",
        "application",
        "applications",
        "backend",
        "built",
        "corp",
        "designed",
        "developer",
        "developed",
        "engineer",
        "experience",
        "frontend",
        "implemented",
        "skills",
        "system",
        "systems",
        "using",
        "with",
    }
)

_HEADING_ALIASES: dict[str, tuple[str, ...]] = {
    "professional summary": ("## professional summary", "## summary"),
    "professional experience": ("## professional experience", "## experience"),
    "skills & abilities": ("## skills & abilities", "## skills"),
    "certifications": ("## certifications",),
    "professional background": ("## professional background", "## background"),
    "education": ("## education",),
}

_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "experience": ("## Selected Experience", "## Rewritten Experience"),
    "projects": ("## Selected Projects", "## Rewritten Projects"),
    "skills": ("## Selected Skills", "## Rewritten Skills"),
}


def sanitize_markdown_output(raw: str) -> str:
    text = raw.strip()
    fence_match = _MARKDOWN_FENCE_PATTERN.match(text)
    if fence_match:
        text = fence_match.group(1).strip()

    if not text:
        raise ValidationError("Resume generator returned empty markdown")

    return text


def finalize_generated_resume(
    markdown: str,
    master_resume: str,
    profile_header: str | None = None,
) -> str:
    header = profile_header or extract_profile_header(master_resume)
    merged = apply_profile_header(markdown, header)
    merged = format_generated_resume(merged, master_resume)
    try:
        reject_generic_placeholders(merged)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    return merged


def extract_template_headings(template: str) -> list[str]:
    headings = _HEADING_PATTERN.findall(template)
    return [heading for heading in headings if "{{" not in heading and "}}" not in heading]


def validate_generated_resume(
    markdown: str,
    template: str,
    selected_experience: str,
    selected_projects: str,
    selected_skills: str,
) -> None:
    template_headings = extract_template_headings(template)
    markdown_lower = markdown.lower()
    for heading in template_headings:
        if heading in markdown:
            continue
        key = heading.removeprefix("## ").strip().lower()
        aliases = _HEADING_ALIASES.get(key, (heading.lower(),))
        if not any(alias in markdown_lower for alias in aliases):
            raise ValidationError(f"Generated resume missing template heading: {heading}")

    unfilled = has_unfilled_template_placeholders(markdown)
    if unfilled:
        raise ValidationError(
            f"Generated resume contains unfilled placeholders: {', '.join(unfilled)}"
        )

    try:
        reject_generic_placeholders(markdown)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    _validate_truthful_sources(
        markdown,
        [selected_experience, selected_projects, selected_skills],
    )


def parse_rewritten_content(text: str) -> ParsedRewrittenContent:
    sections = _split_sections(text)
    return ParsedRewrittenContent(
        selected_experience=_extract_section(sections, "experience"),
        selected_projects=_extract_section(sections, "projects"),
        selected_skills=_extract_section(sections, "skills"),
    )


def _split_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    current_key: str | None = None
    buckets: dict[str, list[str]] = {}

    for line in lines:
        stripped = line.strip()
        matched_key = _match_section_key(stripped)
        if matched_key is not None:
            current_key = matched_key
            buckets.setdefault(current_key, [])
            continue
        if current_key is not None:
            buckets.setdefault(current_key, []).append(line)

    return {key: "\n".join(value).strip() for key, value in buckets.items()}


def _match_section_key(line: str) -> str | None:
    for key, aliases in _SECTION_ALIASES.items():
        if line in aliases:
            return key
    return None


def _extract_section(sections: dict[str, str], key: str) -> str:
    return sections.get(key, "").strip()


def _validate_truthful_sources(markdown: str, sources: list[str]) -> None:
    normalized_output = _normalize_text(markdown)
    all_lines: list[str] = []
    for source in sources:
        all_lines.extend(_substantive_lines(source))

    if not all_lines:
        raise ValidationError("Resume generator requires at least one selected content line")

    if any(_normalize_text(line) in normalized_output for line in all_lines):
        return

    source_tokens = _extract_anchor_tokens("\n".join(all_lines))
    if not source_tokens:
        return

    output_tokens = _extract_anchor_tokens(normalized_output)
    overlap = source_tokens & output_tokens
    min_required = max(2, min(4, len(source_tokens) // 4))
    if len(overlap) >= min_required:
        return

    raise ValidationError(
        "Generated resume must preserve truthful selected content from the provided sections"
    )


def _extract_anchor_tokens(text: str) -> set[str]:
    tokens = _TOKEN_PATTERN.findall(text.lower())
    cleaned = {token.rstrip(".,;:!?") for token in tokens}
    return {
        token
        for token in cleaned
        if (len(token) >= 4 or token in _TECH_SHORT_TOKENS)
        and token not in _GENERIC_RESUME_TOKENS
    }


def _substantive_lines(text: str) -> list[str]:
    lines = [line.strip().lstrip("-*•").strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()
