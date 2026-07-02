from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, APITimeoutError

from app.services.openai_service import OpenAIConfig, OpenAIService


def _make_response(content: str = "tailored resume") -> MagicMock:
    choice = MagicMock()
    choice.message.content = content

    usage = MagicMock()
    usage.prompt_tokens = 100
    usage.completion_tokens = 50
    usage.total_tokens = 150

    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


def _make_config(**overrides: object) -> OpenAIConfig:
    defaults = {
        "api_key": "test-key",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "timeout_seconds": 30.0,
        "max_retries": 3,
        "retry_base_delay_seconds": 0.01,
    }
    defaults.update(overrides)
    return OpenAIConfig(**defaults)


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock()
    client.chat.completions.create = AsyncMock(return_value=_make_response())
    return client


@pytest.mark.asyncio
async def test_generate_returns_completion(mock_client: AsyncMock) -> None:
    service = OpenAIService(_make_config(), client=mock_client)

    result = await service.generate("You are helpful.", "Tailor this resume.")

    assert result == "tailored resume"
    mock_client.chat.completions.create.assert_awaited_once_with(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Tailor this resume."},
        ],
        temperature=0.7,
    )


@pytest.mark.asyncio
async def test_generate_retries_on_timeout(mock_client: AsyncMock) -> None:
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            APITimeoutError(request=MagicMock()),
            _make_response("after retry"),
        ]
    )
    service = OpenAIService(_make_config(max_retries=2), client=mock_client)

    result = await service.generate("system", "user")

    assert result == "after retry"
    assert mock_client.chat.completions.create.await_count == 2


@pytest.mark.asyncio
async def test_generate_raises_after_exhausted_retries(mock_client: AsyncMock) -> None:
    mock_client.chat.completions.create = AsyncMock(
        side_effect=APIConnectionError(request=MagicMock())
    )
    service = OpenAIService(_make_config(max_retries=2), client=mock_client)

    with pytest.raises(APIConnectionError):
        await service.generate("system", "user")

    assert mock_client.chat.completions.create.await_count == 2
