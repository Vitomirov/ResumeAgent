from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeGeneratorInput:
    resume_template: str
    master_resume: str
    profile_header: str
    reference_education: str
    reference_background: str
    selected_experience: str
    selected_projects: str
    selected_skills: str


@dataclass(frozen=True)
class ResumeGeneratorOutput:
    markdown: str


@dataclass(frozen=True)
class ParsedRewrittenContent:
    selected_experience: str
    selected_projects: str
    selected_skills: str
