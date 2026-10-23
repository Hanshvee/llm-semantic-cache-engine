
from openai import AsyncOpenAI

from app.config import config
from app.llm.openai_provider import OpenAIProvider
from app.models.query import QueryRequest
from app.models.llm import LLMResponse
from app.utils.logger import log_llm_call


class GroqProvider(OpenAIProvider):
    """Groq provider using its OpenAI-compatible API."""

    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            requests_per_minute=20,
        )

    def get_name(self) -> str:
        return "groq"

    def _get_client(self) -> AsyncOpenAI:
        if not self._client:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url="https://api.groq.com/openai/v1",
            )
        return self._client

    async def _make_api_call(
        self, request: QueryRequest
    ) -> LLMResponse:
        response = await self._get_client().chat.completions.create(
            model=request.get_model(config.default_model),
            messages=[{"role": "user", "content": request.query}],
            max_tokens=request.get_max_tokens(
                config.default_max_tokens
            ),
            temperature=request.get_temperature(
                config.default_temperature
            ),
        )

        usage = response.usage
        result = LLMResponse(
            content=response.choices[0].message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=response.model,
        )

        log_llm_call(
            provider="groq",
            model=result.model,
            tokens=result.total_tokens,
        )
        return result
