import html
import re
from dataclasses import dataclass

from app.domain.generation.resume_sections import extract_master_section

_MAX_BULLET_LEN = 78
_DATE_PREFIX = re.compile(
    r"^(?P<dates>"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}"
    r"\s*[–-]\s*"
    r"(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"
    r")"
    r"(?:\s*\|\s*(?P<links>.+))?$"
)
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_PROJECT_HEADING = re.compile(r"^#{1,3}\s+(?P<name>.+)$")
_BULLET_LINE = re.compile(r"^[-*•]\s+(?P<text>.+)$")
_SKILL_LABEL = re.compile(r"^\*\*(?P<label>[^:*]+?):?\*\*[:\s]*(?P<values>.*)$")
_LEADING_BULLET = re.compile(r"^[-*•]\s+")
_HTML_ENTRY_BLOCK = re.compile(r'<div class="entry-block">', re.IGNORECASE)
_SIGNIFICANT_TOKEN = re.compile(r"[a-z0-9+#./-]{4,}")


@dataclass(frozen=True)
class ProjectEntry:
    name: str
    role_meta: str
    dates: str
    links_html: str


@dataclass(frozen=True)
class BackgroundEntry:
    title: str
    dates: str


def format_generated_resume(markdown: str, master_resume: str) -> str:
    formatted = _format_profile_header(markdown)
    entries = parse_project_entries(master_resume)
    if entries:
        formatted = _replace_section(
            formatted,
            "Professional Experience",
            lambda body: _format_experience_body(body, entries, master_resume),
        )
    else:
        formatted = compact_all_bullets(formatted)

    background_entries = parse_background_entries(master_resume)
    if background_entries:
        formatted = _replace_section(
            formatted,
            "Professional Background",
            lambda body: _format_background_body(body, background_entries, master_resume),
        )

    formatted = _replace_section(
        formatted,
        ("Skills & Abilities", "Skills"),
        _format_skills_body,
    )

    return formatted


def parse_project_entries(master_resume: str) -> list[ProjectEntry]:
    body = extract_master_section(master_resume, "Professional Experience")
    if not body:
        return []

    entries: list[ProjectEntry] = []
    lines = body.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if not line.startswith("### "):
            index += 1
            continue

        name = line[4:].strip()
        role_meta = ""
        dates = ""
        links_html = ""
        index += 1

        index = _skip_blank_lines(lines, index)
        if index < len(lines) and _is_role_line(lines[index]):
            role_meta = lines[index].strip()
            index += 1

        index = _skip_blank_lines(lines, index)
        if index < len(lines) and _is_date_or_link_line(lines[index]):
            dates, links_html = _parse_dates_and_links(lines[index].strip())
            index += 1

        entries.append(
            ProjectEntry(
                name=name,
                role_meta=role_meta,
                dates=dates,
                links_html=links_html,
            )
        )

    return entries


def parse_background_entries(master_resume: str) -> list[BackgroundEntry]:
    body = extract_master_section(master_resume, "Professional Background")
    if not body:
        return []

    entries: list[BackgroundEntry] = []
    lines = body.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if not line.startswith("### "):
            index += 1
            continue

        title = line[4:].strip()
        dates = ""
        index += 1
        index = _skip_blank_lines(lines, index)

        if index < len(lines) and _DATE_PREFIX.match(lines[index].strip()):
            dates = _DATE_PREFIX.match(lines[index].strip()).group("dates").strip()
            index += 1

        entries.append(BackgroundEntry(title=title, dates=dates))

    return entries


def compact_bullet(text: str, max_len: int = _MAX_BULLET_LEN) -> str:
    cleaned = " ".join(text.split())
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;")

    if ";" in cleaned:
        cleaned = cleaned.split(";", 1)[0].strip()

    if len(cleaned) > max_len and "—" in cleaned:
        cleaned = cleaned.split("—", 1)[0].strip()

    if len(cleaned) <= max_len:
        return cleaned.rstrip(".,;")

    words = cleaned.split()
    kept: list[str] = []
    for word in words:
        candidate = " ".join([*kept, word])
        if len(candidate) > max_len:
            break
        kept.append(word)

    if not kept:
        return cleaned[:max_len].rstrip(".,;")

    return " ".join(kept).rstrip(".,;")


def compact_all_bullets(markdown: str) -> str:
    formatted_lines: list[str] = []
    for line in markdown.splitlines():
        bullet_match = _BULLET_LINE.match(line.strip())
        if bullet_match:
            formatted_lines.append(f"- {compact_bullet(bullet_match.group('text'))}")
        else:
            formatted_lines.append(line)
    return "\n".join(formatted_lines)


def _format_profile_header(markdown: str) -> str:
    lines = markdown.splitlines()
    if not lines or not lines[0].startswith("# "):
        return markdown

    name = lines[0][2:].strip()
    contact_line = ""
    body_start = 1

    for index in range(1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            body_start = index
            break
        if stripped:
            contact_line = stripped
            body_start = index + 1
            break

    header_html = (
        '<div class="resume-header">\n'
        f'<h1 class="resume-name">{html.escape(name)}</h1>\n'
        f'<p class="resume-contact">{_inline_markdown_to_html(contact_line)}</p>\n'
        "</div>"
    )
    remainder = "\n".join(lines[body_start:]).lstrip("\n")
    return f"{header_html}\n\n{remainder}" if remainder else header_html


def _format_experience_body(
    body: str,
    entries: list[ProjectEntry],
    master_resume: str,
) -> str:
    chunks = _split_experience_chunks(body)
    assigned = _assign_chunks_to_entries(chunks, entries, master_resume)
    if not assigned:
        return compact_all_bullets(body)

    return "\n\n".join(
        _render_project_block(entry, bullets) for entry, bullets in assigned
    ).strip()


def _format_background_body(
    body: str,
    entries: list[BackgroundEntry],
    master_resume: str,
) -> str:
    chunks = _split_experience_chunks(body)
    assigned = _assign_background_chunks(chunks, entries, master_resume)
    if not assigned:
        return compact_all_bullets(body)

    blocks: list[str] = []
    for entry, bullets in assigned:
        compacted = [compact_bullet(bullet) for bullet in bullets if bullet.strip()][:3]
        if not compacted:
            compacted = _get_master_bullets(master_resume, "Professional Background", entry.title)[:3]
        blocks.append(_render_background_block(entry, compacted))

    return "\n\n".join(blocks).strip()


def _format_skills_body(body: str) -> str:
    entries = parse_skill_entries(body)
    items = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(values)}</li>"
        for label, values in entries
        if values
    )
    if not items:
        return body
    return f'<ul class="skills-list">{items}</ul>'


def parse_skill_entries(body: str) -> list[tuple[str, str]]:
    """Parse a Skills section into (label, values) pairs.

    Handles both ``### Category`` subsections and ``**Label:** values`` lines.
    """
    entries: list[tuple[str, str]] = []
    current_label: str | None = None
    current_values: list[str] = []

    def flush() -> None:
        nonlocal current_label, current_values
        if current_label:
            values = " ".join(part.strip() for part in current_values if part.strip())
            entries.append((current_label, values.strip(" ,;")))
        current_label = None
        current_values = []

    for raw_line in body.splitlines():
        stripped = _LEADING_BULLET.sub("", raw_line.strip())
        if not stripped:
            continue

        if stripped.startswith("### "):
            flush()
            current_label = stripped[4:].strip()
            continue

        if label_match := _SKILL_LABEL.match(stripped):
            flush()
            current_label = label_match.group("label").strip()
            values = label_match.group("values").strip()
            current_values = [values] if values else []
            continue

        if current_label is not None:
            current_values.append(_strip_html(stripped) if "<" in stripped else stripped)

    flush()
    return entries


def _render_project_block(entry: ProjectEntry, bullets: list[str]) -> str:
    compacted = [compact_bullet(bullet) for bullet in bullets if bullet.strip()][:5]
    links = (
        f'<span class="entry-links">{entry.links_html}</span>'
        if entry.links_html
        else '<span class="entry-links"></span>'
    )
    bullet_items = "".join(
        f"<li>{html.escape(bullet)}</li>" for bullet in compacted
    )
    bullets_html = (
        f'<ul class="entry-bullets">{bullet_items}</ul>' if bullet_items else ""
    )

    return (
        '<div class="entry-block project-entry">\n'
        '<div class="entry-header">\n'
        f'<span class="entry-title"><strong>{html.escape(entry.name)}</strong></span>\n'
        f"{links}\n"
        "</div>\n"
        '<div class="entry-meta">\n'
        f'<span class="entry-role">{html.escape(entry.role_meta)}</span>\n'
        f'<span class="entry-dates">{html.escape(entry.dates)}</span>\n'
        "</div>\n"
        f"{bullets_html}\n"
        "</div>"
    )


def _render_background_block(entry: BackgroundEntry, bullets: list[str]) -> str:
    bullet_items = "".join(
        f"<li>{html.escape(bullet)}</li>" for bullet in bullets if bullet.strip()
    )
    bullets_html = (
        f'<ul class="entry-bullets">{bullet_items}</ul>' if bullet_items else ""
    )

    return (
        '<div class="entry-block background-entry">\n'
        '<div class="entry-header">\n'
        f'<span class="entry-title"><strong>{html.escape(entry.title)}</strong></span>\n'
        f'<span class="entry-dates">{html.escape(entry.dates)}</span>\n'
        "</div>\n"
        f"{bullets_html}\n"
        "</div>"
    )


def _assign_chunks_to_entries(
    chunks: list[tuple[str, list[str]]],
    entries: list[ProjectEntry],
    master_resume: str,
) -> list[tuple[ProjectEntry, list[str]]]:
    assigned: list[tuple[ProjectEntry, list[str]]] = []
    used: set[str] = set()

    for title, bullets in chunks:
        candidates = [
            (_score_project_match(title, bullets, entry, master_resume), entry)
            for entry in entries
            if entry.name not in used
        ]
        if not candidates:
            continue

        score, entry = max(candidates, key=lambda item: item[0])
        if score <= 0:
            continue
        used.add(entry.name)
        final_bullets = bullets or _get_master_bullets(
            master_resume,
            "Professional Experience",
            entry.name,
        )
        assigned.append((entry, final_bullets))

    return assigned


def _assign_background_chunks(
    chunks: list[tuple[str, list[str]]],
    entries: list[BackgroundEntry],
    master_resume: str,
) -> list[tuple[BackgroundEntry, list[str]]]:
    assigned: list[tuple[BackgroundEntry, list[str]]] = []
    used: set[str] = set()

    for title, bullets in chunks:
        candidates = [
            (_score_background_match(title, bullets, entry, master_resume), entry)
            for entry in entries
            if entry.title not in used
        ]
        if not candidates:
            continue

        score, entry = max(candidates, key=lambda item: item[0])
        if score <= 0:
            continue
        used.add(entry.title)
        assigned.append((entry, bullets))

    return assigned


def _score_project_match(
    title: str,
    bullets: list[str],
    entry: ProjectEntry,
    master_resume: str,
) -> float:
    score = 0.0
    normalized_title = _normalize_name(title)
    normalized_entry = _normalize_name(entry.name)

    if normalized_title and normalized_entry:
        if normalized_title == normalized_entry:
            score += 20
        elif normalized_title in normalized_entry or normalized_entry in normalized_title:
            score += 14
        elif _token_overlap(normalized_title, normalized_entry) >= 2:
            score += 8

    master_text = _get_master_bullets(
        master_resume,
        "Professional Experience",
        entry.name,
    )
    master_blob = " ".join(master_text).lower()
    chunk_blob = " ".join(bullets).lower()

    for token in _significant_tokens(chunk_blob):
        if token in master_blob:
            score += 1.5

    for token in _significant_tokens(entry.name):
        if token in chunk_blob or token in normalized_title:
            score += 1.0

    return score


def _score_background_match(
    title: str,
    bullets: list[str],
    entry: BackgroundEntry,
    master_resume: str,
) -> float:
    score = 0.0
    normalized_title = _normalize_name(title)
    normalized_entry = _normalize_name(entry.title)

    if normalized_title and normalized_entry:
        if normalized_title == normalized_entry:
            score += 20
        elif normalized_title in normalized_entry or normalized_entry in normalized_title:
            score += 14

    master_text = _get_master_bullets(
        master_resume,
        "Professional Background",
        entry.title,
    )
    master_blob = " ".join(master_text).lower()
    chunk_blob = " ".join(bullets).lower()

    for token in _significant_tokens(chunk_blob):
        if token in master_blob:
            score += 1.5

    return score


def _get_master_bullets(
    master_resume: str,
    section: str,
    entry_title: str,
) -> list[str]:
    body = extract_master_section(master_resume, section)
    if not body:
        return []

    lines = body.splitlines()
    collecting = False
    bullets: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            name = stripped[4:].strip()
            collecting = _normalize_name(name) == _normalize_name(entry_title)
            continue
        if collecting and (match := _BULLET_LINE.match(stripped)):
            bullets.append(match.group("text"))

    return bullets


def _split_experience_chunks(body: str) -> list[tuple[str, list[str]]]:
    if _HTML_ENTRY_BLOCK.search(body):
        return _split_html_entry_chunks(body)

    chunks: list[tuple[str, list[str]]] = []
    current_title = ""
    current_bullets: list[str] = []

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if heading_match := _PROJECT_HEADING.match(stripped):
            if current_title or current_bullets:
                chunks.append((current_title, current_bullets))
            current_title = heading_match.group("name").strip()
            current_bullets = []
            continue

        if title := _extract_title_from_line(stripped):
            if current_title or current_bullets:
                chunks.append((current_title, current_bullets))
            current_title = title
            current_bullets = []
            continue

        if bullet_match := _BULLET_LINE.match(stripped):
            current_bullets.append(bullet_match.group("text"))
            continue

        if stripped.startswith("<li>") and stripped.endswith("</li>"):
            current_bullets.append(_strip_html(stripped))

    if current_title or current_bullets:
        chunks.append((current_title, current_bullets))

    return chunks


def _split_html_entry_chunks(body: str) -> list[tuple[str, list[str]]]:
    parts = re.split(r'(?=<div class="entry-block">)', body, flags=re.IGNORECASE)
    chunks: list[tuple[str, list[str]]] = []

    for part in parts:
        stripped = part.strip()
        if not stripped:
            continue

        title_match = re.search(
            r'<span class="entry-title"><strong>(?P<name>[^<]+)</strong></span>',
            stripped,
            flags=re.IGNORECASE,
        )
        title = title_match.group("name").strip() if title_match else ""
        bullets = [
            _strip_html(match.group(1))
            for match in re.finditer(r"<li>(?P<text>.*?)</li>", stripped, flags=re.IGNORECASE)
        ]
        bullets.extend(_BULLET_LINE.findall(stripped))
        chunks.append((title, bullets))

    return chunks or _split_experience_chunks(re.sub(r"<[^>]+>", "", body))


def _parse_dates_and_links(line: str) -> tuple[str, str]:
    match = _DATE_PREFIX.match(line.strip())
    if not match:
        return "", _links_to_html(line)

    dates = match.group("dates").strip()
    links = match.group("links") or ""
    return dates, _links_to_html(links)


def _links_to_html(links_text: str) -> str:
    links = _LINK_PATTERN.findall(links_text)
    if not links:
        return ""

    return " / ".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label.strip())}</a>'
        for label, url in links
    )


def _inline_markdown_to_html(text: str) -> str:
    segments = [segment.strip() for segment in text.split("|")]
    rendered: list[str] = []

    for segment in segments:
        if not segment:
            continue
        links = _LINK_PATTERN.findall(segment)
        if links and segment.strip() == f"[{links[0][0]}]({links[0][1]})":
            label, url = links[0]
            rendered.append(
                f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
            )
        else:
            rendered.append(html.escape(segment))

    return " &nbsp;|&nbsp; ".join(rendered)


def _replace_section(
    markdown: str,
    heading: str | tuple[str, ...],
    transform,
) -> str:
    headings = (heading,) if isinstance(heading, str) else heading
    targets = {f"## {name}".lower() for name in headings}
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.strip().lower() in targets:
            output.append(line)
            index += 1
            body_lines: list[str] = []
            while index < len(lines) and not lines[index].startswith("## "):
                body_lines.append(lines[index])
                index += 1
            body = "\n".join(body_lines).strip()
            formatted = transform(body).strip()
            if formatted:
                output.append("")
                output.append(formatted)
            continue

        output.append(line)
        index += 1

    return "\n".join(output)


def _extract_title_from_line(line: str) -> str | None:
    if line.startswith("<div"):
        return None

    if strong_match := re.search(
        r"<strong>(?P<name>[^<]+)</strong>", line, flags=re.IGNORECASE
    ):
        return strong_match.group("name").strip()

    if line.startswith("**") and line.endswith("**"):
        return line.strip("* ").strip()

    if _is_role_line(line) or _is_date_or_link_line(line):
        return None

    return None


def _is_role_line(line: str) -> bool:
    stripped = line.strip()
    return (
        bool(stripped)
        and "|" in stripped
        and not stripped.startswith("-")
        and not stripped.startswith("#")
        and not _DATE_PREFIX.match(stripped)
    )


def _is_date_or_link_line(line: str) -> bool:
    stripped = line.strip()
    if _DATE_PREFIX.match(stripped):
        return True
    return bool(_LINK_PATTERN.search(stripped)) and not stripped.startswith("-")


def _skip_blank_lines(lines: list[str], index: int) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _normalize_name(name: str) -> str:
    lowered = name.lower()
    lowered = re.sub(r"[^\w\s]", "", lowered)
    return " ".join(lowered.split())


def _token_overlap(left: str, right: str) -> int:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    return len(left_tokens & right_tokens)


def _significant_tokens(text: str) -> set[str]:
    return {
        token
        for token in _SIGNIFICANT_TOKEN.findall(text.lower())
        if token not in {"built", "developed", "designed", "implemented", "with", "using"}
    }


def _strip_html(text: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", text)
    return html.unescape(without_tags).strip()
