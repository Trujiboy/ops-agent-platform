"""
Shared Anthropic client with prompt caching configuration.
Usado por todos los módulos del sistema OPS-AGENT.
"""
import os
from functools import lru_cache
from loguru import logger
import anthropic

# Models — Claude 4.x family (actualizado mayo 2026)
SONNET = "claude-sonnet-4-6"
HAIKU  = "claude-haiku-4-5-20251001"


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    """Singleton Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    return anthropic.Anthropic(api_key=api_key)


def create_cached_message(
    system_prompt: str,
    user_content: str,
    large_context: str | None = None,
    model: str = SONNET,
    max_tokens: int = 4096,
) -> str:
    """
    Create a message with prompt caching applied to large_context.

    Args:
        system_prompt: System instructions (not cached — changes per call)
        user_content:  The specific user request
        large_context: Large text to cache (pliego, bid corpus, etc.)
                       Cached 5 min → -90% input token cost on repeated calls
        model:         claude-sonnet-4-6 | claude-haiku-4-5-20251001
        max_tokens:    Max tokens for response

    Cost estimate:
        Sonnet + 10K tokens cached  → ~€0.001/call (vs €0.03 uncached)
        Haiku  + 5K tokens cached   → ~€0.0001/call
    """
    client = get_client()

    messages_content: list[dict] = []

    if large_context:
        messages_content.append({
            "type": "text",
            "text": large_context,
            "cache_control": {"type": "ephemeral"},  # TTL: 5 min
        })

    messages_content.append({"type": "text", "text": user_content})

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": messages_content}],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
        )

        usage = response.usage
        if hasattr(usage, "cache_read_input_tokens") and usage.cache_read_input_tokens:
            logger.debug(
                f"Cache HIT: {usage.cache_read_input_tokens} tokens cached, "
                f"{usage.input_tokens} new tokens"
            )

        return response.content[0].text

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise


def create_structured_message(
    system_prompt: str,
    user_content: str,
    large_context: str | None = None,
    model: str = HAIKU,
    max_tokens: int = 1024,
) -> str:
    """
    Variant for structured JSON output (scoring, classification).
    Uses Haiku by default for cost efficiency.
    Always instructs the model to return pure JSON.
    """
    json_system = (
        system_prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No preamble, "
        "no markdown code blocks, no explanation outside the JSON structure."
    )
    return create_cached_message(
        system_prompt=json_system,
        user_content=user_content,
        large_context=large_context,
        model=model,
        max_tokens=max_tokens,
    )
