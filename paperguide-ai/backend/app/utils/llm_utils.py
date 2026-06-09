"""LLM utilities (placeholder for Phase 2)."""

from ..core import get_logger

logger = get_logger(__name__)


async def call_llm_api(prompt: str, model: str = "gpt-4", **kwargs) -> str:
    """
    Call LLM API with prompt.
    
    TODO: Implement in Phase 2
    """
    logger.info(f"LLM API call - TODO: Implement in Phase 2")
    # TODO: Initialize LLM client (OpenAI, etc.)
    # TODO: Format prompt
    # TODO: Call API
    # TODO: Handle errors and retries
    # TODO: Return response
    return ""


async def embed_text(text: str) -> list[float]:
    """
    Get embeddings for text.
    
    TODO: Implement in Phase 2
    """
    logger.info(f"Text embedding - TODO: Implement in Phase 2")
    # TODO: Call embedding API
    # TODO: Return embeddings
    return []
