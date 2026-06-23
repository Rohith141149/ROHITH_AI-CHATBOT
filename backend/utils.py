import functools
import logging

from fastapi import HTTPException

from config import CONTENT_PREVIEW_LENGTH

logger = logging.getLogger(__name__)


def handle_endpoint_errors(func):
    """Decorator that wraps endpoint logic with consistent error handling."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("%s endpoint error", func.__name__)
            raise HTTPException(
                status_code=500,
                detail="An internal error occurred. Please try again later.",
            )

    return wrapper


def content_summary(content, preview_length=CONTENT_PREVIEW_LENGTH):
    """Return a dict with character count and a truncated preview."""
    return {
        "characters": len(content),
        "preview": content[:preview_length],
    }
