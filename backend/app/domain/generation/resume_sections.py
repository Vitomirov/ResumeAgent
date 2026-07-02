import re

_HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
_FORBIDDEN_PLACEHOLDERS = (
    "[your name]",
    "[your contact information]",
    "[your education information]",
)


def extract_profile_header(master_resume: str) -> str:
    """Return the name + contact block from the top of the master resume."""
    lines: list[str] = []
    for line in master_resume.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped:
            lines.append(stripped)
    if not lines:
        raise ValueError("Master resume must start with a name and contact block")
    return "\n".join(lines)


def extract_master_section(master_resume: str, *headings: str) -> str:
    """Extract body text for the first matching ## heading in the master resume."""
    normalized = {heading.lower(): heading for heading in headings}
    current: str | None = None
    buckets: dict[str, list[str]] = {}

    for line in master_resume.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            key = title.lower()
            current = key if key in normalized else None
            if current is not None:
                buckets.setdefault(current, [])
            continue
        if current is not None:
            buckets.setdefault(current, []).append(line)

    for heading in headings:
        key = heading.lower()
        if key in buckets:
            return "\n".join(buckets[key]).strip()
    return ""


def apply_profile_header(resume_markdown: str, profile_header: str) -> str:
    """Replace any generated header with the canonical profile block."""
    match = re.search(r"^## .+$", resume_markdown.strip(), re.MULTILINE)
    if not match:
        return profile_header

    body = resume_markdown.strip()[match.start() :]
    return f"{profile_header}\n\n{body}"


def reject_generic_placeholders(markdown: str) -> None:
    lowered = markdown.lower()
    for placeholder in _FORBIDDEN_PLACEHOLDERS:
        if placeholder in lowered:
            raise ValueError("Generated resume contains generic placeholders")


def has_unfilled_template_placeholders(markdown: str) -> list[str]:
    return re.findall(r"\{\{[^}]+\}\}", markdown)
