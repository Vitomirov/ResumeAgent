from pydantic import BaseModel, Field


class TextContent(BaseModel):
    content: str = Field(default="")


class TailorRequest(BaseModel):
    job_description: str = Field(min_length=1)


class PreviewResponse(BaseModel):
    run_id: str
    markdown: str


class AtsScoreResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)


class TailorResponse(BaseModel):
    run_id: str
    markdown: str
    ats_score: AtsScoreResponse


class ExportRequest(BaseModel):
    run_id: str = Field(min_length=1)


class ExportResponse(BaseModel):
    run_id: str
    pdf_path: str
