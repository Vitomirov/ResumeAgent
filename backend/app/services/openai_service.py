import asyncio
import logging
from dataclasses import dataclass

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

logger = logging.getLogger(__name__)

RETRYABLE_EXCEPTIONS = (APITimeoutError, APIConnectionError, RateLimitError)


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str
    temperature: float
    timeout_seconds: float
    max_retries: int
    retry_base_delay_seconds: float


class OpenAIService:
    """Isolated OpenAI chat completion client."""

    def __init__(self, config: OpenAIConfig, client: AsyncOpenAI | None = None) -> None:
        self._config = config
        self._client = client or AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout_seconds,
            max_retries=0,
        )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self._config.max_retries + 1):
            try:
                return await self._create_completion(system_prompt, user_prompt)
            except RETRYABLE_EXCEPTIONS as exc:
                last_error = exc
                if attempt >= self._config.max_retries:
                    break
                delay = self._config.retry_base_delay_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "OpenAI request failed (attempt %s/%s), retrying in %.1fs: %s",
                    attempt,
                    self._config.max_retries,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
            except APIError as exc:
                if exc.status_code is not None and exc.status_code >= 500:
                    last_error = exc
                    if attempt >= self._config.max_retries:
                        break
                    delay = self._config.retry_base_delay_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "OpenAI server error (attempt %s/%s), retrying in %.1fs: %s",
                        attempt,
                        self._config.max_retries,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise

        assert last_error is not None
        raise last_error

    async def _create_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._config.temperature,
        )

        usage = response.usage
        if usage is not None:
            logger.info(
                "OpenAI token usage model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
                self._config.model,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned empty completion content")

        return content
