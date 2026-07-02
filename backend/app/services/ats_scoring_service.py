import re
from dataclasses import dataclass

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "this",
        "to",
        "we",
        "will",
        "with",
        "you",
        "your",
        "our",
        "all",
        "any",
        "can",
        "able",
        "work",
        "working",
        "role",
        "team",
        "using",
        "use",
        "used",
        "including",
        "include",
        "required",
        "requirements",
        "experience",
        "years",
        "year",
        "strong",
        "skills",
        "skill",
        "looking",
        "join",
        "help",
        "build",
        "support",
        "backend",
        "engineer",
        "developer",
        "must",
        "know",
        "preferred",
        "plus",
        "job",
        "position",
        "candidate",
        "candidates",
        "apply",
        "applicants",
        "company",
        "employer",
        "employment",
        "benefits",
        "compensation",
        "salary",
        "hybrid",
        "remote",
        "office",
        "location",
        "equal",
        "opportunity",
        "discriminate",
        "disability",
        "disabilities",
        "veteran",
        "veterans",
        "minority",
        "minorities",
        "women",
        "gender",
        "identity",
        "orientation",
        "protected",
        "accommodation",
        "reasonable",
        "diversity",
        "inclusion",
        "culture",
        "values",
        "mission",
        "vision",
        "about",
        "who",
        "what",
        "where",
        "when",
        "how",
        "also",
        "such",
        "those",
        "these",
        "other",
        "others",
        "well",
        "being",
        "health",
        "wellness",
        "mental",
        "paid",
        "time",
        "off",
        "vacation",
        "bonus",
        "perks",
        "offer",
        "offers",
        "offering",
        "program",
        "programs",
        "intern",
        "interns",
        "internship",
        "full",
        "part",
        "term",
        "month",
        "months",
        "week",
        "days",
        "day",
        "start",
        "starting",
        "today",
        "future",
        "growing",
        "great",
        "exciting",
        "passion",
        "passionate",
        "enthusiasm",
        "eager",
        "dedicated",
        "committed",
        "professional",
        "environment",
        "workplace",
        "organization",
        "teamwork",
        "collaboration",
        "collaborate",
        "communicate",
        "communication",
        "problem",
        "solving",
        "learning",
        "growth",
        "career",
        "advancement",
        "opportunities",
        "opportunity",
    }
)

_TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")
_HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)


@dataclass(frozen=True)
class AtsScoreResult:
    score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    total_keywords: int


class AtsScoringService:
    """Keyword overlap between extracted job requirements and the tailored resume."""

    _MAX_MISSING_DISPLAY = 20

    def score(
        self,
        technical_requirements: str,
        soft_skills: str,
        resume_markdown: str,
    ) -> AtsScoreResult:
        keywords = self._extract_keywords(technical_requirements) | self._extract_keywords(
            soft_skills
        )
        if not keywords:
            return AtsScoreResult(
                score=0,
                matched_keywords=[],
                missing_keywords=[],
                total_keywords=0,
            )

        resume_text = resume_markdown.lower()
        matched = sorted(keyword for keyword in keywords if keyword in resume_text)
        missing = sorted(keyword for keyword in keywords if keyword not in resume_text)
        score = round(len(matched) / len(keywords) * 100)

        return AtsScoreResult(
            score=score,
            matched_keywords=matched,
            missing_keywords=missing[: self._MAX_MISSING_DISPLAY],
            total_keywords=len(keywords),
        )

    def _extract_keywords(self, text: str) -> set[str]:
        if not text.strip():
            return set()

        body = self._strip_headings(text)
        tokens = _TOKEN_PATTERN.findall(body.lower())
        cleaned = {token.rstrip(".,;:!?") for token in tokens}
        return {
            token
            for token in cleaned
            if self._is_relevant_keyword(token)
        }

    def _strip_headings(self, text: str) -> str:
        return _HEADING_PATTERN.sub(" ", text)

    def _is_relevant_keyword(self, token: str) -> bool:
        if len(token) < 2 or token in _STOPWORDS:
            return False
        if token.replace(".", "").isdigit():
            return False
        if len(token) <= 2 and token not in {"ai", "ci", "ui", "ux", "db", "qa", "go", "js"}:
            return False
        return True
