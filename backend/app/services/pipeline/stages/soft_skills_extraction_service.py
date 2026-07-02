from app.domain.pipeline.models import SoftSkillsInput, SoftSkillsOutput
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class SoftSkillsExtractionService:
    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def execute(self, input_data: SoftSkillsInput) -> SoftSkillsOutput:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.EXTRACT_SOFT_SKILLS,
            job_description=input_data.job_description,
            job_analysis=input_data.job_analysis,
        )
        soft_skills = await self._openai.generate(system_prompt, user_prompt)
        return SoftSkillsOutput(soft_skills=soft_skills)
