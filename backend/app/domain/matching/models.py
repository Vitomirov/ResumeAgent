from pydantic import BaseModel, Field, field_validator


class RankedSection(BaseModel):
    section_id: str = Field(min_length=1)
    section_title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    relevance_score: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    @field_validator("matched_keywords")
    @classmethod
    def strip_keywords(cls, value: list[str]) -> list[str]:
        return [keyword.strip() for keyword in value if keyword.strip()]


class ResumeMatchResult(BaseModel):
    sections: list[RankedSection] = Field(default_factory=list)
    total_sections_in_resume: int = Field(ge=0)
    matched_section_count: int = Field(ge=0)
    matching_notes: str = Field(default="")

    @field_validator("sections")
    @classmethod
    def sort_by_relevance(cls, sections: list[RankedSection]) -> list[RankedSection]:
        return sorted(sections, key=lambda section: section.relevance_score, reverse=True)
