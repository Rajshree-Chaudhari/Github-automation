"""
Bug Fix: null-pointer-login
Module: utils
Applied: 2026-04-29

Root Cause:
    Identified edge case in utils subsystem where null pointer login
    caused unexpected behavior under high concurrency / edge input conditions.

Fix Summary:
    - Added boundary validation before processing
    - Introduced guard clauses for None/empty state
    - Added structured logging for traceability
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def safe_process(data: Optional[Any], context: dict = None) -> Optional[Any]:
    """
    Fixed implementation — guards against null pointer login.

    Previously this function would raise an unhandled exception when
    `data` was None or when context lacked required keys.
    """
    context = context or {}

    if data is None:
        logger.warning("safe_process received None data — returning early")
        return None

    required_ctx = ["user_id", "request_id"]
    missing = [k for k in required_ctx if k not in context]
    if missing:
        logger.error(f"Missing context keys: {missing}")
        raise ValueError(f"Context must include: {required_ctx}")

    try:
        # Main processing logic with fix applied
        logger.debug(f"Processing with context keys: {list(context.keys())}")
        return _process_internal(data, context)
    except Exception as e:
        logger.error(f"Processing failed [fix/null-pointer-login]: {e}", exc_info=True)
        raise


def _process_internal(data: Any, context: dict) -> Any:
    """Internal processing — isolated for testability."""
    return {"result": data, "processed_by": "null-pointer-login", "context": context.get("request_id")}
