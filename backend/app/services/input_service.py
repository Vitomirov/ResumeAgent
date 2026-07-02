from app.core.paths import MASTER_RESUME_PATH, TEMPLATE_PATH
from app.ports.storage_port import StoragePort


class InputService:
    def __init__(self, storage: StoragePort) -> None:
        self._storage = storage

    def get_master_resume(self) -> str:
        return self._storage.read_text(MASTER_RESUME_PATH)

    def get_template(self) -> str:
        return self._storage.read_text(TEMPLATE_PATH)

    def save_master_resume(self, content: str) -> None:
        self._storage.write_text(MASTER_RESUME_PATH, content)

    def save_template(self, content: str) -> None:
        self._storage.write_text(TEMPLATE_PATH, content)
