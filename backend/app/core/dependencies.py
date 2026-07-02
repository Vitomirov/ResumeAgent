from functools import lru_cache

from app.adapters.filesystem_storage import FilesystemStorage
from app.adapters.markdown_pdf_renderer import MarkdownPDFRenderer
from app.core.config import settings
from app.services.ats_scoring_service import AtsScoringService
from app.services.export_service import ExportService
from app.services.generation.resume_generator import ResumeGenerator
from app.services.input_service import InputService
from app.services.matching.resume_matching_engine import ResumeMatchingEngine
from app.services.openai_service import OpenAIConfig, OpenAIService
from app.services.pipeline.coordinator import PipelineCoordinator
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
from app.services.preview_service import PreviewService
from app.services.prompt_repository import PromptRepository
from app.services.tailor_service import TailorService


@lru_cache
def get_storage() -> FilesystemStorage:
    return FilesystemStorage(base_dir=settings.data_dir)


@lru_cache
def get_openai_service() -> OpenAIService:
    return OpenAIService(
        OpenAIConfig(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
            retry_base_delay_seconds=settings.openai_retry_base_delay_seconds,
        )
    )


@lru_cache
def get_prompt_repository() -> PromptRepository:
    return PromptRepository(prompts_dir=settings.prompts_dir)


@lru_cache
def get_pdf_renderer() -> MarkdownPDFRenderer:
    return MarkdownPDFRenderer()


@lru_cache
def get_ats_scoring_service() -> AtsScoringService:
    return AtsScoringService()


@lru_cache
def get_resume_matching_engine() -> ResumeMatchingEngine:
    return ResumeMatchingEngine(
        openai=get_openai_service(),
        prompts=get_prompt_repository(),
    )


@lru_cache
def get_resume_generator() -> ResumeGenerator:
    return ResumeGenerator(
        openai=get_openai_service(),
        prompts=get_prompt_repository(),
    )


def _openai_prompt_service[T](service_type: type[T]) -> T:
    return service_type(openai=get_openai_service(), prompts=get_prompt_repository())


@lru_cache
def get_job_description_analysis_service() -> JobDescriptionAnalysisService:
    return _openai_prompt_service(JobDescriptionAnalysisService)


@lru_cache
def get_technical_requirements_extraction_service() -> TechnicalRequirementsExtractionService:
    return _openai_prompt_service(TechnicalRequirementsExtractionService)


@lru_cache
def get_soft_skills_extraction_service() -> SoftSkillsExtractionService:
    return _openai_prompt_service(SoftSkillsExtractionService)


@lru_cache
def get_content_rewrite_service() -> ContentRewriteService:
    return _openai_prompt_service(ContentRewriteService)


@lru_cache
def get_section_matching_service() -> SectionMatchingService:
    return SectionMatchingService(matching_engine=get_resume_matching_engine())


@lru_cache
def get_resume_generation_service() -> ResumeGenerationService:
    return ResumeGenerationService(resume_generator=get_resume_generator())


@lru_cache
def get_pipeline_coordinator() -> PipelineCoordinator:
    return PipelineCoordinator(
        job_description_analysis=get_job_description_analysis_service(),
        technical_requirements_extraction=get_technical_requirements_extraction_service(),
        soft_skills_extraction=get_soft_skills_extraction_service(),
        section_matching=get_section_matching_service(),
        content_rewrite=get_content_rewrite_service(),
        resume_generation=get_resume_generation_service(),
    )


def get_input_service() -> InputService:
    return InputService(storage=get_storage())


def get_tailor_service() -> TailorService:
    return TailorService(
        storage=get_storage(),
        input_service=get_input_service(),
        pipeline=get_pipeline_coordinator(),
        ats_scoring=get_ats_scoring_service(),
    )


def get_preview_service() -> PreviewService:
    return PreviewService(storage=get_storage())


def get_export_service() -> ExportService:
    return ExportService(storage=get_storage(), pdf_renderer=get_pdf_renderer())
