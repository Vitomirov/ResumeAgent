from app.domain.pipeline.models import JobDescriptionAnalysisInput, JobDescriptionAnalysisOutput
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class JobDescriptionAnalysisService:
    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def execute(
        self, input_data: JobDescriptionAnalysisInput
    ) -> JobDescriptionAnalysisOutput:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.ANALYZE_JOB,
            job_description=input_data.job_description,
        )
        analysis = await self._openai.generate(system_prompt, user_prompt)
        return JobDescriptionAnalysisOutput(analysis=analysis)
