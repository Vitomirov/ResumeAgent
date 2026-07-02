from app.domain.pipeline.models import TechnicalRequirementsInput, TechnicalRequirementsOutput
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class TechnicalRequirementsExtractionService:
    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def execute(self, input_data: TechnicalRequirementsInput) -> TechnicalRequirementsOutput:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.EXTRACT_REQUIREMENTS,
            job_description=input_data.job_description,
            job_analysis=input_data.job_analysis,
        )
        requirements = await self._openai.generate(system_prompt, user_prompt)
        return TechnicalRequirementsOutput(requirements=requirements)
