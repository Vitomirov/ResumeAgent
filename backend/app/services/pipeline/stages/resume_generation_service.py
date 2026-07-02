from app.domain.generation.models import ResumeGeneratorInput
from app.domain.pipeline.models import ResumeGenerationInput, ResumeGenerationOutput
from app.services.generation.resume_generator import ResumeGenerator


class ResumeGenerationService:
    def __init__(self, resume_generator: ResumeGenerator) -> None:
        self._resume_generator = resume_generator

    async def execute(self, input_data: ResumeGenerationInput) -> ResumeGenerationOutput:
        result = await self._resume_generator.generate(
            ResumeGeneratorInput(
                resume_template=input_data.resume_template,
                master_resume=input_data.master_resume,
                profile_header=input_data.profile_header,
                reference_education=input_data.reference_education,
                reference_background=input_data.reference_background,
                reference_certifications=input_data.reference_certifications,
                selected_experience=input_data.selected_experience,
                selected_projects=input_data.selected_projects,
                selected_skills=input_data.selected_skills,
            )
        )
        return ResumeGenerationOutput(final_resume=result.markdown)
