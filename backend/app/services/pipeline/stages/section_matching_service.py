from app.domain.pipeline.models import SectionMatchingInput, SectionMatchingOutput
from app.services.matching.resume_matching_engine import ResumeMatchingEngine


class SectionMatchingService:
    def __init__(self, matching_engine: ResumeMatchingEngine) -> None:
        self._matching_engine = matching_engine

    async def execute(self, input_data: SectionMatchingInput) -> SectionMatchingOutput:
        match_result = await self._matching_engine.match(
            master_resume=input_data.master_resume,
            job_description=input_data.job_description,
        )
        return SectionMatchingOutput(
            match_result=match_result,
            matched_sections=match_result.model_dump_json(indent=2),
        )
