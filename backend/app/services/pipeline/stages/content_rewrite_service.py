from app.domain.generation.experience_formatter import compact_all_bullets
from app.domain.generation.policies import parse_rewritten_content
from app.domain.pipeline.models import ContentRewriteInput, ContentRewriteOutput
from app.services.openai_service import OpenAIService
from app.services.pipeline import prompt_names
from app.services.prompt_repository import PromptRepository


class ContentRewriteService:
    def __init__(self, openai: OpenAIService, prompts: PromptRepository) -> None:
        self._openai = openai
        self._prompts = prompts

    async def execute(self, input_data: ContentRewriteInput) -> ContentRewriteOutput:
        system_prompt, user_prompt = self._prompts.render(
            prompt_names.REWRITE_RESUME,
            matched_sections=input_data.matched_sections,
            job_analysis=input_data.job_analysis,
            technical_requirements=input_data.technical_requirements,
            soft_skills=input_data.soft_skills,
        )
        rewritten_content = await self._openai.generate(system_prompt, user_prompt)
        parsed = parse_rewritten_content(rewritten_content)
        return ContentRewriteOutput(
            selected_experience=compact_all_bullets(parsed.selected_experience),
            selected_projects=compact_all_bullets(parsed.selected_projects),
            selected_skills=parsed.selected_skills,
        )
