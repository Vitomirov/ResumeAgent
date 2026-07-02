import json
import re

from app.domain.errors import ValidationError
from app.domain.matching.models import ResumeMatchResult

_JSON_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()


def parse_json_response(raw: str) -> dict:
    text = raw.strip()
    fence_match = _JSON_FENCE_PATTERN.match(text)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError("Matching engine returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise ValidationError("Matching engine JSON root must be an object")

    return payload


def validate_match_result(
    result: ResumeMatchResult,
    master_resume: str,
    job_description: str,
) -> None:
    if result.matched_section_count != len(result.sections):
        raise ValidationError(
            "matched_section_count must equal the number of ranked sections returned"
        )

    if not result.sections:
        raise ValidationError("Matching engine must return at least one relevant section")

    normalized_resume = normalize_text(master_resume)
    normalized_job = normalize_text(job_description)

    for section in result.sections:
        _validate_section_content(section.content, normalized_resume)
        _validate_keywords(
            section.matched_keywords,
            normalized_job,
            section.content,
            normalized_resume,
        )


def _validate_section_content(content: str, normalized_resume: str) -> None:
    lines = [line.strip().lstrip("-*•").strip() for line in content.splitlines()]
    substantive_lines = [line for line in lines if line]

    if not substantive_lines:
        raise ValidationError("Section content must include verbatim resume text")

    for line in substantive_lines:
        if normalize_text(line) not in normalized_resume:
            raise ValidationError(
                "Section content must be copied verbatim from the master resume; "
                f"no match found for: {line[:120]}"
            )


def _validate_keywords(
    keywords: list[str],
    normalized_job: str,
    content: str,
    normalized_resume: str,
) -> None:
    normalized_content = normalize_text(content)
    combined_text = f"{normalized_job} {normalized_content} {normalized_resume}"

    for keyword in keywords:
        if not _keyword_is_grounded(keyword, combined_text):
            raise ValidationError(
                f"Matched keyword must appear in the job description or resume content: {keyword}"
            )


def _keyword_is_grounded(keyword: str, combined_text: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return True

    if normalized_keyword in combined_text:
        return True

    if normalized_keyword.endswith("s") and normalized_keyword[:-1] in combined_text:
        return True

    if f"{normalized_keyword}s" in combined_text:
        return True

    tokens = [token for token in normalized_keyword.split() if len(token) >= 2]
    if len(tokens) <= 1:
        return False

    return all(_token_in_text(token, combined_text) for token in tokens)


def _token_in_text(token: str, text: str) -> bool:
    if token in text:
        return True

    if token.endswith("s") and token[:-1] in text:
        return True

    if f"{token}s" in text:
        return True

    return False
