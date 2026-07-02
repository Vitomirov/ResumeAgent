import logging

from app.domain.generation.certifications import select_reference_certifications
from app.domain.generation.resume_sections import (
    extract_master_section,
    extract_profile_header,
    omit_template_section,
)
from app.domain.pipeline.models import (
    ContentRewriteInput,
    JobDescriptionAnalysisInput,
    PipelineInput,
    PipelineOutput,
    ResumeGenerationInput,
    SectionMatchingInput,
    SoftSkillsInput,
    TechnicalRequirementsInput,
)
from app.services.pipeline.stages.content_rewrite_service import ContentRewriteService
from app.services.pipeline.stages.job_description_analysis_service import (
    JobDescriptionAnalysisService,
)
from app.services.pipeline.stages.resume_generation_service import ResumeGenerationService
from app.services.pipeline.stages.section_matching_service import SectionMatchingService
from app.services.pipeline.stages.soft_skills_extraction_service import SoftSkillsExtractionService
from app.services.pipeline.stages.technical_requirements_extraction_service import (
    TechnicalRequirementsExtractionService,
)

logger = logging.getLogger(__name__)


class PipelineCoordinator:
    """Orchestrates pipeline stages. Stages are independent and unaware of each other."""

    def __init__(
        self,
        job_description_analysis: JobDescriptionAnalysisService,
        technical_requirements_extraction: TechnicalRequirementsExtractionService,
        soft_skills_extraction: SoftSkillsExtractionService,
        section_matching: SectionMatchingService,
        content_rewrite: ContentRewriteService,
        resume_generation: ResumeGenerationService,
    ) -> None:
        self._job_description_analysis = job_description_analysis
        self._technical_requirements_extraction = technical_requirements_extraction
        self._soft_skills_extraction = soft_skills_extraction
        self._section_matching = section_matching
        self._content_rewrite = content_rewrite
        self._resume_generation = resume_generation

    async def run(self, input_data: PipelineInput) -> PipelineOutput:
        logger.info("Pipeline stage 1: analyzing job description")
        analysis = await self._job_description_analysis.execute(
            JobDescriptionAnalysisInput(job_description=input_data.job_description)
        )

        logger.info("Pipeline stage 2: extracting technical requirements")
        technical = await self._technical_requirements_extraction.execute(
            TechnicalRequirementsInput(
                job_description=input_data.job_description,
                job_analysis=analysis.analysis,
            )
        )

        logger.info("Pipeline stage 3: extracting soft skills")
        soft_skills = await self._soft_skills_extraction.execute(
            SoftSkillsInput(
                job_description=input_data.job_description,
                job_analysis=analysis.analysis,
            )
        )

        logger.info("Pipeline stage 4: matching master resume sections")
        matched = await self._section_matching.execute(
            SectionMatchingInput(
                master_resume=input_data.master_resume,
                job_description=input_data.job_description,
            )
        )

        logger.info("Pipeline stage 5: rewriting selected content")
        rewritten = await self._content_rewrite.execute(
            ContentRewriteInput(
                matched_sections=matched.matched_sections,
                job_analysis=analysis.analysis,
                technical_requirements=technical.requirements,
                soft_skills=soft_skills.soft_skills,
            )
        )

        logger.info("Pipeline stage 6: generating final resume")
        profile_header = extract_profile_header(input_data.master_resume)
        reference_education = extract_master_section(
            input_data.master_resume,
            "Education",
        )
        reference_background = extract_master_section(
            input_data.master_resume,
            "Professional Background",
        )
        reference_certifications = select_reference_certifications(
            input_data.master_resume,
            input_data.job_description,
            job_analysis=analysis.analysis,
            technical_requirements=technical.requirements,
        )
        resume_template = input_data.resume_template
        if not reference_certifications.strip():
            resume_template = omit_template_section(resume_template, "Certifications")
        final = await self._resume_generation.execute(
            ResumeGenerationInput(
                resume_template=resume_template,
                master_resume=input_data.master_resume,
                profile_header=profile_header,
                reference_education=reference_education,
                reference_background=reference_background,
                reference_certifications=reference_certifications,
                selected_experience=rewritten.selected_experience,
                selected_projects=rewritten.selected_projects,
                selected_skills=rewritten.selected_skills,
            )
        )

        logger.info("Pipeline complete")
        return PipelineOutput(
            final_resume=final.final_resume,
            technical_requirements=technical.requirements,
            soft_skills=soft_skills.soft_skills,
        )
