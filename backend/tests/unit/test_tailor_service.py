import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.adapters.filesystem_storage import FilesystemStorage
from app.domain.pipeline.models import PipelineOutput
from app.services.ats_scoring_service import AtsScoringService
from app.services.input_service import InputService
from app.services.tailor_service import TailorService


@pytest.mark.asyncio
async def test_tailor_service_persists_output(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)
    storage.write_text(Path("inputs/master_resume.md"), "# Master Resume")
    storage.write_text(Path("inputs/resume_template.md"), "# {{ summary }}")

    pipeline = AsyncMock()
    pipeline.run = AsyncMock(
        return_value=PipelineOutput(
            final_resume="# Tailored Resume",
            technical_requirements="## Required Technical Skills\n- Python",
            soft_skills="## Soft Skills\n- Collaboration",
        )
    )

    service = TailorService(
        storage=storage,
        input_service=InputService(storage=storage),
        pipeline=pipeline,
        ats_scoring=AtsScoringService(),
    )
    result = await service.tailor("Looking for a Python developer.")

    assert result["markdown"] == "# Tailored Resume"
    assert result["run_id"]
    assert "ats_score" in result

    run_dir = tmp_path / "outputs" / result["run_id"]
    assert (run_dir / "tailored_resume.md").read_text(encoding="utf-8") == "# Tailored Resume"

    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["run_id"] == result["run_id"]
    assert metadata["job_description_length"] == len("Looking for a Python developer.")

    pipeline.run.assert_awaited_once()
