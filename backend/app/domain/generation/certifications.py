from dataclasses import dataclass

from app.domain.generation.resume_sections import extract_master_subsections

_FRONTEND_KEYWORDS = (
    "frontend",
    "front-end",
    "front end",
    "ui developer",
    "ui engineer",
    "ux developer",
    "react developer",
    "react.js",
    "vue",
    "angular",
    "bootstrap",
    "css",
    "html",
    "web developer",
    "javascript developer",
    "responsive design",
    "tailwind",
    "mobile-first",
    "component library",
)

_AI_KEYWORDS = (
    " ai ",
    "artificial intelligence",
    "machine learning",
    " llm",
    "llms",
    "openai",
    "prompt engineer",
    "generative ai",
    "gen ai",
    "ai engineer",
    "ai developer",
    "ml engineer",
    "cursor ai",
    "cursor ",
    "chatgpt",
    "gpt-",
    "gpt4",
    "ai bootcamp",
    "vibe coding",
    "ai-native",
    "llm integration",
)


@dataclass(frozen=True)
class CertificationEntry:
    heading: str
    role_categories: frozenset[str]


CERTIFICATION_ENTRIES: tuple[CertificationEntry, ...] = (
    CertificationEntry(
        heading="The Ultimate Bootstrap Guide - Bootstrap 5 from Scratch",
        role_categories=frozenset({"frontend"}),
    ),
    CertificationEntry(
        heading="Skills for UkisAI - 5 Week AI Bootcamp (Vibe Coding)",
        role_categories=frozenset({"ai"}),
    ),
)


def detect_role_categories(*texts: str) -> set[str]:
    combined = " ".join(text.strip() for text in texts if text.strip()).lower()
    categories: set[str] = set()

    if any(keyword in combined for keyword in _FRONTEND_KEYWORDS):
        categories.add("frontend")
    if any(keyword in combined for keyword in _AI_KEYWORDS):
        categories.add("ai")

    return categories


def select_reference_certifications(
    master_resume: str,
    job_description: str,
    *,
    job_analysis: str = "",
    technical_requirements: str = "",
) -> str:
    categories = detect_role_categories(
        job_description,
        job_analysis,
        technical_requirements,
    )
    if not categories:
        return ""

    subsections = extract_master_subsections(master_resume, "Certifications")
    selected: list[str] = []

    for entry in CERTIFICATION_ENTRIES:
        if not entry.role_categories & categories:
            continue
        body = subsections.get(entry.heading, "").strip()
        if body:
            selected.append(f"### {entry.heading}\n\n{body}")

    return "\n\n".join(selected)
