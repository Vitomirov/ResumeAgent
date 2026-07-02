from abc import ABC, abstractmethod
from pathlib import Path


class StoragePort(ABC):
    @abstractmethod
    def read_text(self, path: Path) -> str:
        raise NotImplementedError

    @abstractmethod
    def write_text(self, path: Path, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, path: Path) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def write_bytes(self, path: Path, content: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_subdirs(self, path: Path) -> list[str]:
        raise NotImplementedError
