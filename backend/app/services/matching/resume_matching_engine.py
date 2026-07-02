from app.domain.matching.models import ResumeMatchResult
from app.domain.matching.policies import parse_json_response, validate_match_result
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class ResumeMatchingEngine:
    """Ranks master resume sections by relevance to a job description."""

    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def match(self, master_resume: str, job_description: str) -> ResumeMatchResult:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.MATCH_RESUME,
            master_resume=master_resume,
            job_description=job_description,
        )
        raw_response = await self._openai.generate(system_prompt, user_prompt)
        payload = parse_json_response(raw_response)
        result = ResumeMatchResult.model_validate(payload)
        validate_match_result(result, master_resume, job_description)
        return result
