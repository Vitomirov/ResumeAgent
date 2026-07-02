from pathlib import Path

from app.ports.storage_port import StoragePort


class FilesystemStorage(StoragePort):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir.resolve()

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    def _resolve(self, path: Path) -> Path:
        if path.is_absolute():
            resolved = path.resolve()
        else:
            resolved = (self._base_dir / path).resolve()

        if not str(resolved).startswith(str(self._base_dir)):
            raise ValueError(f"Path escapes storage base directory: {path}")

        return resolved

    def read_text(self, path: Path) -> str:
        target = self._resolve(path)
        return target.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def read_bytes(self, path: Path) -> bytes:
        return self._resolve(path).read_bytes()

    def write_bytes(self, path: Path, content: bytes) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def exists(self, path: Path) -> bool:
        return self._resolve(path).exists()

    def list_subdirs(self, path: Path) -> list[str]:
        target = self._resolve(path)
        if not target.is_dir():
            return []

        return sorted(
            (entry.name for entry in target.iterdir() if entry.is_dir()),
            key=lambda name: (target / name).stat().st_mtime,
            reverse=True,
        )
