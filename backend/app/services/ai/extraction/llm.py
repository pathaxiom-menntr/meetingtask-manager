"""
extraction/llm.py — Azure OpenAI call with exponential-backoff retry.

Single responsibility: send a message list to the LLM, retry on failure,
return a parsed dict. Nothing else.
"""

import json
import time

from openai import APIError, APITimeoutError, RateLimitError

from app.core.logger import get_logger
from ..client import client
from ..config import MAX_RETRIES

logger = get_logger(__name__)


def call_llm(
    messages: list[dict],
    temperature: float = 0.05,
    max_retries: int = MAX_RETRIES,
) -> dict:
    """
    Call Azure OpenAI with exponential-backoff retry logic.

    Retries on:
    - APIError (server-side errors)
    - APITimeoutError (network timeout)
    - RateLimitError (throttling)
    - json.JSONDecodeError (malformed response)

    Raises RuntimeError after all attempts are exhausted.
    """
    from app.core.config import settings

    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Azure OpenAI")
            return json.loads(content)

        except (APIError, APITimeoutError, RateLimitError) as e:
            last_error = e
            wait = 2 ** attempt  # 2s, 4s, 8s
            logger.warning(
                "Azure OpenAI API error (attempt %d/%d): %s — retrying in %ds",
                attempt, max_retries, e, wait,
            )
            time.sleep(wait)

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning("JSON decode error (attempt %d/%d): %s", attempt, max_retries, e)
            if attempt < max_retries:
                time.sleep(1)

        except Exception as e:
            last_error = e
            logger.error("Unexpected LLM error (attempt %d/%d): %s", attempt, max_retries, e)
            if attempt < max_retries:
                time.sleep(1)

    raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_error}")
