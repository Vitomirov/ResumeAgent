from app.domain.generation.models import ResumeGeneratorInput, ResumeGeneratorOutput
from app.domain.generation.policies import (
    finalize_generated_resume,
    sanitize_markdown_output,
    validate_generated_resume,
)
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class ResumeGenerator:
    """Assembles a tailored resume from a template and selected content."""

    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def generate(self, input_data: ResumeGeneratorInput) -> ResumeGeneratorOutput:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.GENERATE_RESUME,
            resume_template=input_data.resume_template,
            reference_education=input_data.reference_education,
            reference_background=input_data.reference_background,
            reference_certifications=input_data.reference_certifications,
            selected_experience=input_data.selected_experience,
            selected_projects=input_data.selected_projects,
            selected_skills=input_data.selected_skills,
        )
        raw_response = await self._openai.generate(system_prompt, user_prompt)
        markdown = sanitize_markdown_output(raw_response)
        markdown = finalize_generated_resume(
            markdown,
            input_data.master_resume,
            input_data.profile_header,
        )
        validate_generated_resume(
            markdown,
            input_data.resume_template,
            input_data.selected_experience,
            input_data.selected_projects,
            input_data.selected_skills,
        )
        return ResumeGeneratorOutput(markdown=markdown)
