from openai import AsyncOpenAI

from app.core.config import settings

# Works with Ollama locally and with any OpenAI-compatible API in production.
client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


async def embed(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(model=settings.embedding_model, input=texts)
    return [item.embedding for item in response.data]
