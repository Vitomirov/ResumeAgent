from app.core.paths import OUTPUTS_DIR, TAILORED_MARKDOWN
from app.domain.errors import NotFoundError
from app.ports.storage_port import StoragePort


class PreviewService:
    def __init__(self, storage: StoragePort) -> None:
        self._storage = storage

    def get_latest(self) -> dict[str, str]:
        for run_id in self._storage.list_subdirs(OUTPUTS_DIR):
            markdown_path = OUTPUTS_DIR / run_id / TAILORED_MARKDOWN
            if self._storage.exists(markdown_path):
                return self.get_by_run_id(run_id)

        raise NotFoundError("No tailored resumes found")

    def get_by_run_id(self, run_id: str) -> dict[str, str]:
        markdown_path = OUTPUTS_DIR / run_id / TAILORED_MARKDOWN
        if not self._storage.exists(markdown_path):
            raise NotFoundError(f"Tailored resume not found for run_id: {run_id}")
        return {
            "run_id": run_id,
            "markdown": self._storage.read_text(markdown_path),
        }
