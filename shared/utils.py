"""
Utilidades compartidas entre módulos.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger


def load_env() -> None:
    """Load .env from repo root. Call once at entry point."""
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.debug(f".env loaded from {env_path}")
    else:
        logger.warning(f".env not found at {env_path} — relying on system env vars")


def require_env(key: str) -> str:
    """Get required env var or raise clearly."""
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file."
        )
    return val


def truncate(text: str, max_chars: int = 200) -> str:
    """Truncate text for logging."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"... [{len(text) - max_chars} chars truncated]"
