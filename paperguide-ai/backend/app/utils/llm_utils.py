"""LLM utilities — OpenAI-compatible API calls."""

from typing import Optional

from ..core import get_logger
from ..core.config import settings

logger = get_logger(__name__)

# Lazy-loaded client so the module is importable even without the openai package.
_client = None


def _get_client():
    """Return (or create) the OpenAI client, configured from settings."""
    global _client
    if _client is not None:
        return _client

    try:
        from openai import AsyncOpenAI
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        return None

    kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL

    _client = AsyncOpenAI(**kwargs)
    return _client


async def call_llm_api(
    prompt: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    **kwargs,
) -> str:
    """Call an OpenAI-compatible chat-completion API.

    Args:
        prompt: The user message / main prompt.
        model: Model name (defaults to ``settings.OPENAI_MODEL``).
        system_prompt: Optional system-level instruction.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum tokens in the response.
        **kwargs: Passed through to the API call.

    Returns:
        The assistant's text response, or an empty string on failure.
    """
    client = _get_client()
    if client is None:
        logger.warning("LLM client not available — returning empty response.")
        return ""

    model = model or settings.OPENAI_MODEL

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""

    except Exception as exc:
        logger.error(f"LLM API call failed: {exc}")
        return ""


async def embed_text(text: str) -> list[float]:
    """Get embeddings for text via OpenAI-compatible API.

    Args:
        text: The text to embed.

    Returns:
        Embedding vector as a list of floats, or empty list on failure.
    """
    client = _get_client()
    if client is None:
        return []

    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.error(f"Embedding call failed: {exc}")
        return []
