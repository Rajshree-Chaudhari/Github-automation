#!/usr/bin/env python3
"""
Retry utility with exponential backoff and jitter.
"""

import functools
import logging
import random
import time
from typing import Callable, Tuple, Type

logger = logging.getLogger("retry")


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator: retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for each successive wait.
        jitter: Add randomness to prevent thundering herd.
        exceptions: Tuple of exception types to catch and retry.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"[{func.__name__}] Failed after {max_retries} retries: {e}")
                        raise

                    wait = backoff_factor**attempt
                    if jitter:
                        wait += random.uniform(0, wait * 0.3)

                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)

            raise last_exception

        return wrapper

    return decorator
