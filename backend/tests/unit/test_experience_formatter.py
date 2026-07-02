from pathlib import Path
import re

from app.domain.generation.experience_formatter import (
    ProjectEntry,
    _assign_chunks_to_entries,
    compact_bullet,
    format_generated_resume,
    parse_project_entries,
)

MASTER = Path(__file__).resolve().parents[3].joinpath("data/inputs/master_resume.md").read_text(
    encoding="utf-8"
)


def test_parse_project_entries_reads_dates_and_links() -> None:
    entries = parse_project_entries(MASTER)
    by_name = {entry.name: entry for entry in entries}

    crate = by_name["AiCrateDigger"]
    assert crate.dates == "Mar 2026 – Present"
    assert 'href="https://aicratedigger.dejanvitomirov.com/"' in crate.links_html
    assert 'href="https://github.com/Vitomirov/AiCrateDigger"' in crate.links_html
    assert "AI Engineer / Fullstack Developer" in crate.role_meta

    rpg = by_name["Backend Microservices Platform (Distributed RPG System)"]
    assert rpg.dates == "Oct 2025 – Mar 2026"
    assert "live demo" not in rpg.links_html
    assert "source code" in rpg.links_html


def test_compact_bullet_removes_parentheticals_and_limits_length() -> None:
    text = (
        "Built FastAPI backend (Python 3.11+, Pydantic v2, SQLAlchemy 2.0 async, httpx) "
        "with single-call search orchestration and explicit failure states (e.g. album_unresolved)"
    )
    compacted = compact_bullet(text)
    assert "(" not in compacted
    assert len(compacted) <= 78


def test_format_generated_resume_injects_project_header_and_dates() -> None:
    generated = """## Professional Summary

AI engineer summary.

## Professional Experience

### AiCrateDigger

- Built production AI search platform for physical music listings across regional record shops
- Designed async pipeline with LLM parsing, Tavily retrieval, and structured JSON extraction

## Skills & Abilities

**AI:** OpenAI
"""

    formatted = format_generated_resume(generated, MASTER)

    assert '<div class="entry-block project-entry">' in formatted
    assert "<strong>AiCrateDigger</strong>" in formatted
    assert 'class="entry-dates">Mar 2026 – Present</span>' in formatted
    assert "aicratedigger.dejanvitomirov.com" in formatted
    assert "github.com/Vitomirov/AiCrateDigger" in formatted
    assert "AI Engineer / Fullstack Developer" in formatted
    assert all(len(compact_bullet(line.strip("- "))) <= 88 for line in formatted.splitlines() if line.strip().startswith("- "))


def test_format_generated_resume_compacts_html_list_bullets() -> None:
    generated = """## Professional Experience

<div class="entry-block">
<div class="entry-header">
<span class="entry-title"><strong>Warranty Wallet</strong></span>
</div>
<ul class="entry-bullets">
<li>Built production full-stack warranty platform for digitizing PDF receipts, tracking expiration dates, automated reminders, and one-click seller claims</li>
</ul>
</div>
"""

    formatted = format_generated_resume(generated, MASTER)

    assert "Jul 2024 – May 2025" in formatted
    assert "warrantywallet" in formatted
    assert "Fullstack Developer" in formatted
    bullet_match = re.search(r"<li>(.*?)</li>", formatted)
    assert bullet_match is not None
    assert len(bullet_match.group(1)) <= 78


def test_format_matches_renamed_project_to_canonical_entry() -> None:
    generated = """## Professional Experience

### AI Search Platform

- Built production AI search platform for vinyl listings with Tavily retrieval
- Designed LLM intent parsing and structured JSON extraction pipeline
- Implemented Redis caching and PostgreSQL store registry for search performance
"""

    formatted = format_generated_resume(generated, MASTER)

    assert "<strong>AiCrateDigger</strong>" in formatted
    assert "Mar 2026 – Present" in formatted
    assert "aicratedigger.dejanvitomirov.com" in formatted
    assert 'class="entry-role"' in formatted
    assert "<ul class=\"entry-bullets\">" in formatted


def test_format_profile_header_is_centered_html() -> None:
    generated = """# Dejan Vitomirov

Pancevo | [GitHub](https://github.com/Vitomirov)

## Professional Summary

Summary text.
"""

    formatted = format_generated_resume(generated, MASTER)

    assert '<div class="resume-header">' in formatted
    assert '<h1 class="resume-name">Dejan Vitomirov</h1>' in formatted
    assert 'class="resume-contact"' in formatted


def test_assign_chunks_handles_tied_scores_without_type_error() -> None:
    entries = [
        ProjectEntry(name="Project A", role_meta="", dates="", links_html=""),
        ProjectEntry(name="Project B", role_meta="", dates="", links_html=""),
    ]
    chunks = [("Unknown Title", ["generic unrelated bullet text"])]

    assigned = _assign_chunks_to_entries(chunks, entries, "")

    assert assigned == []
