from abc import ABC, abstractmethod


class PDFRendererPort(ABC):
    @abstractmethod
    def render(self, markdown: str) -> bytes:
        raise NotImplementedError
