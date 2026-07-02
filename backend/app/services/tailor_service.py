import json
import uuid
from datetime import UTC, datetime

from app.core.paths import METADATA_JSON, OUTPUTS_DIR, TAILORED_MARKDOWN
from app.domain.pipeline.models import PipelineInput
from app.ports.storage_port import StoragePort
from app.services.ats_scoring_service import AtsScoringService
from app.services.input_service import InputService
from app.services.pipeline.coordinator import PipelineCoordinator


class TailorService:
    def __init__(
        self,
        storage: StoragePort,
        input_service: InputService,
        pipeline: PipelineCoordinator,
        ats_scoring: AtsScoringService,
    ) -> None:
        self._storage = storage
        self._input_service = input_service
        self._pipeline = pipeline
        self._ats_scoring = ats_scoring

    async def tailor(self, job_description: str) -> dict:
        master_resume = self._input_service.get_master_resume()
        resume_template = self._input_service.get_template()

        result = await self._pipeline.run(
            PipelineInput(
                job_description=job_description,
                master_resume=master_resume,
                resume_template=resume_template,
            )
        )

        ats = self._ats_scoring.score(
            result.technical_requirements,
            result.soft_skills,
            result.final_resume,
        )

        run_id = uuid.uuid4().hex
        run_dir = OUTPUTS_DIR / run_id
        self._storage.write_text(run_dir / TAILORED_MARKDOWN, result.final_resume)
        self._storage.write_text(
            run_dir / METADATA_JSON,
            json.dumps(
                {
                    "run_id": run_id,
                    "created_at": datetime.now(UTC).isoformat(),
                    "job_description_length": len(job_description),
                    "ats_score": ats.score,
                    "total_keywords": ats.total_keywords,
                    "matched_keywords": ats.matched_keywords,
                    "missing_keywords": ats.missing_keywords,
                },
                indent=2,
            ),
        )

        return {
            "run_id": run_id,
            "markdown": result.final_resume,
            "ats_score": {
                "score": ats.score,
                "total_keywords": ats.total_keywords,
                "matched_keywords": ats.matched_keywords,
                "missing_keywords": ats.missing_keywords,
            },
        }
