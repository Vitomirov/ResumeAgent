from app.services.ats_scoring_service import AtsScoringService


def test_ats_score_uses_requirements_not_boilerplate() -> None:
    service = AtsScoringService()
    requirements = """## Required Technical Skills
- Python, FastAPI, PostgreSQL

## Tools & Platforms
- Docker, Git
"""
    soft_skills = """## Soft Skills
- Problem-solving, collaboration
"""
    resume = """# Jane Doe

## Professional Summary

Python backend engineer with FastAPI, PostgreSQL, Docker, and Git experience.

## Skills & Abilities

**Backend:** Python, FastAPI, PostgreSQL
"""

    result = service.score(requirements, soft_skills, resume)

    assert result.score >= 70
    assert "python" in result.matched_keywords
    assert "fastapi" in result.matched_keywords
    assert "discriminate" not in result.missing_keywords
    assert "veterans" not in result.missing_keywords


def test_ats_score_reports_missing_requirements() -> None:
    service = AtsScoringService()
    requirements = """## Required Technical Skills
- Python, Kubernetes, Terraform
"""
    resume = "## Skills\n\nPython\n"

    result = service.score(requirements, "", resume)

    assert result.score < 100
    assert "python" in result.matched_keywords
    assert "kubernetes" in result.missing_keywords
    assert "terraform" in result.missing_keywords
