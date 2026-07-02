from dataclasses import dataclass

from app.domain.matching.models import ResumeMatchResult


@dataclass(frozen=True)
class PipelineInput:
    job_description: str
    master_resume: str
    resume_template: str


@dataclass(frozen=True)
class PipelineOutput:
    final_resume: str
    technical_requirements: str
    soft_skills: str


@dataclass(frozen=True)
class JobDescriptionAnalysisInput:
    job_description: str


@dataclass(frozen=True)
class JobDescriptionAnalysisOutput:
    analysis: str


@dataclass(frozen=True)
class TechnicalRequirementsInput:
    job_description: str
    job_analysis: str


@dataclass(frozen=True)
class TechnicalRequirementsOutput:
    requirements: str


@dataclass(frozen=True)
class SoftSkillsInput:
    job_description: str
    job_analysis: str


@dataclass(frozen=True)
class SoftSkillsOutput:
    soft_skills: str


@dataclass(frozen=True)
class SectionMatchingInput:
    master_resume: str
    job_description: str


@dataclass(frozen=True)
class SectionMatchingOutput:
    match_result: ResumeMatchResult
    matched_sections: str


@dataclass(frozen=True)
class ContentRewriteInput:
    matched_sections: str
    job_analysis: str
    technical_requirements: str
    soft_skills: str


@dataclass(frozen=True)
class ContentRewriteOutput:
    selected_experience: str
    selected_projects: str
    selected_skills: str


@dataclass(frozen=True)
class ResumeGenerationInput:
    resume_template: str
    master_resume: str
    profile_header: str
    reference_education: str
    reference_background: str
    reference_certifications: str
    selected_experience: str
    selected_projects: str
    selected_skills: str


@dataclass(frozen=True)
class ResumeGenerationOutput:
    final_resume: str
