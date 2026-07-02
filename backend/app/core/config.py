from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_root_env() -> Path:
    """Resolve project root .env (shared with frontend and Docker Compose)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".env").exists() or (parent / ".env.example").exists():
            if (parent / "docker-compose.yml").exists() or (parent / "Makefile").exists():
                return parent
    return Path.cwd()


_ROOT = _find_root_env()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_timeout_seconds: float = 60.0
    openai_max_retries: int = 3
    openai_retry_base_delay_seconds: float = 1.0

    prompts_dir: Path = _ROOT / "prompts"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    data_dir: Path = _ROOT / "data"

    cors_origins: list[str] = ["http://localhost:3000"]
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    @property
    def inputs_dir(self) -> Path:
        return self.data_dir / "inputs"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    @property
    def config_dir(self) -> Path:
        return self.data_dir / "config"

    @field_validator("data_dir", "prompts_dir", mode="after")
    @classmethod
    def resolve_relative_paths(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return (_ROOT / value).resolve()


settings = Settings()
