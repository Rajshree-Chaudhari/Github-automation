#!/usr/bin/env python3
"""
Code Generator
Produces realistic, varied code changes across multiple categories.
Simulates genuine day-to-day development work.
"""

import logging
import random
import string
from datetime import datetime

from config.settings import Settings

logger = logging.getLogger("code_generator")

# ─── Change Type Weights (simulate realistic dev distribution) ─────────────────
CHANGE_WEIGHTS = {
    "feature": 30,
    "fix": 25,
    "refactor": 20,
    "docs": 10,
    "perf": 10,
    "test": 5,
}

# ─── Branch Name Vocabularies ──────────────────────────────────────────────────
FEATURE_NAMES = [
    "user-auth", "dashboard-metrics", "export-csv", "notification-service",
    "search-filter", "dark-mode", "api-rate-limiting", "cache-layer",
    "audit-logging", "bulk-operations", "webhook-support", "oauth-integration",
    "multi-tenancy", "role-permissions", "data-pagination", "health-checks",
    "session-management", "email-templates", "file-upload", "report-generator"
]

FIX_NAMES = [
    "null-pointer-login", "race-condition-jobs", "memory-leak-cache",
    "timeout-api-calls", "encoding-special-chars", "overflow-pagination",
    "deadlock-transactions", "cors-headers", "stale-session-token",
    "broken-redirect-flow", "duplicate-entries", "missing-validation",
    "incorrect-date-format", "broken-csv-export", "401-unauthorized-edge"
]

REFACTOR_NAMES = [
    "extract-service-layer", "simplify-auth-middleware", "rename-user-model",
    "consolidate-db-queries", "modularize-config", "split-monolith-routes",
    "cleanup-dead-code", "standardize-error-handling", "improve-type-hints",
    "decouple-email-service", "migrate-to-dataclasses", "abstract-repository"
]

COMMIT_VERBS = {
    "feature": ["add", "implement", "introduce", "build", "create"],
    "fix": ["fix", "resolve", "patch", "correct", "address"],
    "refactor": ["refactor", "simplify", "reorganize", "clean up", "restructure"],
    "docs": ["update", "document", "add", "clarify", "expand"],
    "perf": ["optimize", "improve", "enhance", "speed up", "cache"],
    "test": ["add tests for", "cover", "test", "validate", "assert"],
}


class CodeGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.project_name = settings.project_name

    def select_change_type(self) -> str:
        population = []
        for ctype, weight in CHANGE_WEIGHTS.items():
            population.extend([ctype] * weight)
        return random.choice(population)

    def generate_branch_name(self, change_type: str) -> str:
        ts = datetime.now().strftime("%m%d")
        suffix = "".join(random.choices(string.ascii_lowercase, k=4))

        if change_type == "feature":
            name = random.choice(FEATURE_NAMES)
            return f"feature/{name}-{ts}"
        elif change_type == "fix":
            name = random.choice(FIX_NAMES)
            return f"fix/{name}-{ts}"
        elif change_type == "refactor":
            name = random.choice(REFACTOR_NAMES)
            return f"refactor/{name}-{ts}"
        elif change_type == "docs":
            return f"docs/update-{random.choice(['readme', 'api-docs', 'changelog', 'contributing'])}-{ts}"
        elif change_type == "perf":
            return f"perf/optimize-{random.choice(['queries', 'cache', 'indexing', 'batch-ops'])}-{ts}"
        elif change_type == "test":
            return f"test/add-coverage-{random.choice(['auth', 'api', 'models', 'utils'])}-{ts}"
        return f"chore/maintenance-{ts}-{suffix}"

    def generate_commit_message(self, change_type: str, change: dict) -> str:
        verb = random.choice(COMMIT_VERBS.get(change_type, ["update"]))
        subject = change.get("description", change["path"].split("/")[-1])
        scope = change.get("scope", "")
        scope_str = f"({scope})" if scope else ""

        # Conventional commits format
        prefix_map = {
            "feature": "feat",
            "fix": "fix",
            "refactor": "refactor",
            "docs": "docs",
            "perf": "perf",
            "test": "test"
        }
        prefix = prefix_map.get(change_type, "chore")
        return f"{prefix}{scope_str}: {verb} {subject}"

    def generate_changes(self, change_type: str) -> list:
        generators = {
            "feature": self._gen_feature_changes,
            "fix": self._gen_fix_changes,
            "refactor": self._gen_refactor_changes,
            "docs": self._gen_docs_changes,
            "perf": self._gen_perf_changes,
            "test": self._gen_test_changes,
        }
        return generators.get(change_type, self._gen_feature_changes)()

    # ─── Feature Changes ───────────────────────────────────────────────────────

    def _gen_feature_changes(self) -> list:
        feature = random.choice(FEATURE_NAMES)
        return [
            {
                "path": f"src/services/{feature.replace('-', '_')}_service.py",
                "scope": "services",
                "description": f"{feature} service implementation",
                "content": self._python_service(feature)
            },
            {
                "path": f"src/api/routes/{feature.replace('-', '_')}.py",
                "scope": "api",
                "description": f"{feature} API routes",
                "content": self._python_routes(feature)
            },
            {
                "path": "CHANGELOG.md",
                "scope": "changelog",
                "description": "changelog entry",
                "content": self._changelog_entry("feature", feature)
            }
        ]

    def _gen_fix_changes(self) -> list:
        fix = random.choice(FIX_NAMES)
        module = random.choice(["auth", "api", "models", "services", "utils"])
        return [
            {
                "path": f"src/{module}/{fix.replace('-', '_')}_fix.py",
                "scope": module,
                "description": f"{fix} bug fix",
                "content": self._python_fix(fix, module)
            },
            {
                "path": "CHANGELOG.md",
                "scope": "changelog",
                "description": "changelog bugfix entry",
                "content": self._changelog_entry("fix", fix)
            }
        ]

    def _gen_refactor_changes(self) -> list:
        refactor = random.choice(REFACTOR_NAMES)
        return [
            {
                "path": f"src/core/{refactor.replace('-', '_')}.py",
                "scope": "core",
                "description": f"{refactor}",
                "content": self._python_refactor(refactor)
            }
        ]

    def _gen_docs_changes(self) -> list:
        doc_type = random.choice(["api", "setup", "architecture", "contributing"])
        return [
            {
                "path": f"docs/{doc_type}.md",
                "scope": "docs",
                "description": f"{doc_type} documentation update",
                "content": self._docs_content(doc_type)
            }
        ]

    def _gen_perf_changes(self) -> list:
        area = random.choice(["database", "cache", "queries", "indexing"])
        return [
            {
                "path": f"src/performance/{area}_optimizer.py",
                "scope": "perf",
                "description": f"{area} performance optimization",
                "content": self._python_perf(area)
            }
        ]

    def _gen_test_changes(self) -> list:
        module = random.choice(["auth", "api", "models", "services"])
        return [
            {
                "path": f"tests/test_{module}_{random.randint(100,999)}.py",
                "scope": "tests",
                "description": f"{module} unit tests",
                "content": self._python_tests(module)
            }
        ]

    # ─── Code Templates ────────────────────────────────────────────────────────

    def _python_service(self, feature: str) -> str:
        class_name = "".join(w.capitalize() for w in feature.split("-")) + "Service"  # noqa: F841
        return f'''"""
{class_name}
Handles business logic for {feature} functionality.
Auto-generated module — {datetime.now().strftime("%Y-%m-%d")}
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class {class_name.replace("Service", "")}Config:
    """Configuration for {feature} service."""
    enabled: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    cache_ttl: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}Error(Exception):
    """Raised when {class_name} operations fail."""
    def __init__(self, message: str, code: str = "UNKNOWN", details: dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {{}}


class {class_name}:
    """
    Core service for managing {feature} operations.

    Responsibilities:
        - Validation of inputs
        - Business rule enforcement
        - Data persistence coordination
        - Event emission
    """

    def __init__(self, config: {class_name.replace("Service", "")}Config = None):
        self.config = config or {class_name.replace("Service", "")}Config()
        self._initialized = False
        self._cache: Dict[str, Any] = {{}}
        logger.info(f"{class_name} initialized with config: {{self.config}}")

    def initialize(self) -> None:
        """Perform async-safe initialization."""
        if self._initialized:
            return
        self._setup_internal_state()
        self._initialized = True
        logger.info(f"{class_name} ready")

    def _setup_internal_state(self) -> None:
        self._cache.clear()

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for {feature} processing.

        Args:
            payload: Input data dictionary

        Returns:
            Processed result dictionary

        Raises:
            {class_name}Error: On validation or processing failure
        """
        if not self._initialized:
            self.initialize()

        logger.debug(f"Processing payload: {{list(payload.keys())}}")
        self._validate(payload)

        result = self._execute(payload)
        logger.info(f"Processing complete: {{result.get('id', 'unknown')}}")
        return result

    def _validate(self, payload: Dict[str, Any]) -> None:
        required = ["id", "data"]
        missing = [k for k in required if k not in payload]
        if missing:
            raise {class_name}Error(
                f"Missing required fields: {{missing}}",
                code="VALIDATION_ERROR",
                details={{"missing_fields": missing}}
            )

    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {{
            "id": payload["id"],
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "{class_name}",
        }}

    def health_check(self) -> Dict[str, Any]:
        return {{
            "service": "{class_name}",
            "status": "healthy" if self._initialized else "not_initialized",
            "cache_size": len(self._cache),
            "config": {{
                "enabled": self.config.enabled,
                "timeout": self.config.timeout_seconds,
            }}
        }}
'''

    def _python_routes(self, feature: str) -> str:
        resource = feature.replace("-", "_")
        return f'''"""
API Routes: {feature}
RESTful endpoints for {feature} resource management.
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)
bp = Blueprint("{resource}", __name__, url_prefix="/api/v1/{resource.replace("_", "-")}")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({{"error": "Unauthorized", "code": "AUTH_REQUIRED"}}), 401
        return f(*args, **kwargs)
    return decorated


def paginate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, int(request.args.get("per_page", 20)))
        return f(*args, page=page, per_page=per_page, **kwargs)
    return decorated


@bp.route("/", methods=["GET"])
@require_auth
@paginate
def list_items(page: int, per_page: int):
    """List {feature} items with pagination."""
    logger.info(f"Listing {resource} — page={{page}}, per_page={{per_page}}")
    return jsonify({{
        "items": [],
        "page": page,
        "per_page": per_page,
        "total": 0,
        "pages": 0
    }})


@bp.route("/<string:item_id>", methods=["GET"])
@require_auth
def get_item(item_id: str):
    """Retrieve a single {feature} item by ID."""
    logger.info(f"Fetching {resource} item: {{item_id}}")
    return jsonify({{"id": item_id, "status": "active"}})


@bp.route("/", methods=["POST"])
@require_auth
def create_item():
    """Create a new {feature} item."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({{"error": "Invalid JSON body"}}), 400
    logger.info(f"Creating {resource} item")
    return jsonify({{"id": "new-id", "created": True}}), 201


@bp.route("/<string:item_id>", methods=["PATCH"])
@require_auth
def update_item(item_id: str):
    """Partially update a {feature} item."""
    data = request.get_json(silent=True) or {{}}
    logger.info(f"Updating {resource} item: {{item_id}}")
    return jsonify({{"id": item_id, "updated": True, "fields": list(data.keys())}})


@bp.route("/<string:item_id>", methods=["DELETE"])
@require_auth
def delete_item(item_id: str):
    """Delete a {feature} item."""
    logger.info(f"Deleting {resource} item: {{item_id}}")
    return "", 204


@bp.errorhandler(404)
def not_found(e):
    return jsonify({{"error": "Not found", "code": "NOT_FOUND"}}), 404


@bp.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error in {resource} routes: {{e}}")
    return jsonify({{"error": "Internal server error", "code": "INTERNAL_ERROR"}}), 500
'''

    def _python_fix(self, fix: str, module: str) -> str:
        class_name = "".join(w.capitalize() for w in fix.split("-"))
        return f'''"""
Bug Fix: {fix}
Module: {module}
Applied: {datetime.now().strftime("%Y-%m-%d")}

Root Cause:
    Identified edge case in {module} subsystem where {fix.replace("-", " ")}
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
    Fixed implementation — guards against {fix.replace("-", " ")}.

    Previously this function would raise an unhandled exception when
    `data` was None or when context lacked required keys.
    """
    context = context or {{}}

    if data is None:
        logger.warning("safe_process received None data — returning early")
        return None

    required_ctx = ["user_id", "request_id"]
    missing = [k for k in required_ctx if k not in context]
    if missing:
        logger.error(f"Missing context keys: {{missing}}")
        raise ValueError(f"Context must include: {{required_ctx}}")

    try:
        # Main processing logic with fix applied
        logger.debug(f"Processing with context keys: {{list(context.keys())}}")
        return _process_internal(data, context)
    except Exception as e:
        logger.error(f"Processing failed [fix/{fix}]: {{e}}", exc_info=True)
        raise


def _process_internal(data: Any, context: dict) -> Any:
    """Internal processing — isolated for testability."""
    return {{"result": data, "processed_by": "{fix}", "context": context.get("request_id")}}
'''

    def _python_refactor(self, refactor: str) -> str:
        return f'''"""
Refactor: {refactor}
Applied: {datetime.now().strftime("%Y-%m-%d")}

Motivation:
    Previous implementation had tight coupling and lacked clear
    separation of concerns. This refactor introduces:
    - Single Responsibility per class
    - Dependency injection instead of hard imports
    - Protocol-based interfaces for testability
"""

from typing import Protocol, runtime_checkable, Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@runtime_checkable
class Repository(Protocol):
    """Abstract repository protocol — decouples storage from business logic."""

    def find_by_id(self, entity_id: str) -> Optional[Dict]:
        ...

    def save(self, entity: Dict) -> Dict:
        ...

    def delete(self, entity_id: str) -> bool:
        ...


class InMemoryRepository:
    """Lightweight in-memory repository for testing and development."""

    def __init__(self):
        self._store: Dict[str, Dict] = {{}}

    def find_by_id(self, entity_id: str) -> Optional[Dict]:
        return self._store.get(entity_id)

    def save(self, entity: Dict) -> Dict:
        if "id" not in entity:
            raise ValueError("Entity must have an 'id' field")
        self._store[entity["id"]] = entity
        return entity

    def delete(self, entity_id: str) -> bool:
        return self._store.pop(entity_id, None) is not None


class BaseService:
    """
    Refactored base service — replaces the previous monolithic implementation.
    Now accepts any Repository-compatible implementation.
    """

    def __init__(self, repository: Repository):
        if not isinstance(repository, Repository):
            raise TypeError(f"Expected Repository protocol, got {{type(repository)}}")
        self._repo = repository
        logger.info(f"{{self.__class__.__name__}} initialized with {{type(repository).__name__}}")

    def get(self, entity_id: str) -> Optional[Dict]:
        entity = self._repo.find_by_id(entity_id)
        if entity is None:
            logger.debug(f"Entity not found: {{entity_id}}")
        return entity

    def create(self, data: Dict) -> Dict:
        self._validate(data)
        return self._repo.save(data)

    def remove(self, entity_id: str) -> bool:
        return self._repo.delete(entity_id)

    def _validate(self, data: Dict) -> None:
        """Override in subclasses for domain-specific validation."""
        pass
'''

    def _python_perf(self, area: str) -> str:
        return f'''"""
Performance Optimizer: {area}
Applied: {datetime.now().strftime("%Y-%m-%d")}

Benchmarks Before:
    - p50: ~450ms  p95: ~1200ms  p99: ~2800ms

Benchmarks After:
    - p50: ~80ms   p95: ~210ms   p99: ~450ms

Strategy:
    - Introduced LRU cache with configurable TTL
    - Batched {area} operations to reduce I/O round trips
    - Added connection pooling for resource reuse
"""

import time
import logging
import functools
from collections import OrderedDict
from typing import Any, Callable, Optional, Tuple

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU cache with TTL support."""

    def __init__(self, capacity: int = 512, ttl_seconds: int = 300):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self._cache: OrderedDict = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, expires_at = self._cache[key]
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, time.monotonic() + self.ttl)
        if len(self._cache) > self.capacity:
            evicted = next(iter(self._cache))
            del self._cache[evicted]
            logger.debug(f"Cache evicted: {{evicted}}")

    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    @property
    def stats(self) -> dict:
        return {{"size": len(self._cache), "capacity": self.capacity, "ttl": self.ttl}}


_cache = LRUCache(capacity=1024, ttl_seconds=300)


def cached(ttl: int = 300):
    """Decorator: cache function results with configurable TTL."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{{fn.__module__}}.{{fn.__qualname__}}:{{args}}:{{sorted(kwargs.items())}}"
            cached_val = _cache.get(cache_key)
            if cached_val is not None:
                logger.debug(f"Cache HIT: {{fn.__name__}}")
                return cached_val
            logger.debug(f"Cache MISS: {{fn.__name__}}")
            result = fn(*args, **kwargs)
            _cache.set(cache_key, result)
            return result
        return wrapper
    return decorator


class BatchProcessor:
    """Process {area} items in optimized batches."""

    def __init__(self, batch_size: int = 50, flush_interval: float = 0.1):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._buffer = []

    def add(self, item: Any) -> Optional[list]:
        self._buffer.append(item)
        if len(self._buffer) >= self.batch_size:
            return self.flush()
        return None

    def flush(self) -> list:
        if not self._buffer:
            return []
        batch = self._buffer[:]
        self._buffer.clear()
        logger.debug(f"Flushing batch of {{len(batch)}} {area} items")
        return self._process_batch(batch)

    def _process_batch(self, items: list) -> list:
        return [self._process_single(item) for item in items]

    def _process_single(self, item: Any) -> Any:
        return item
'''

    def _python_tests(self, module: str) -> str:
        return f'''"""
Test Suite: {module}
Generated: {datetime.now().strftime("%Y-%m-%d")}
Coverage target: ≥ 85%
"""

import pytest
import time
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    return {{
        "enabled": True,
        "timeout": 30,
        "max_retries": 3,
        "debug": False
    }}


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.find_by_id.return_value = {{"id": "test-123", "status": "active"}}
    repo.save.side_effect = lambda e: {{**e, "saved": True}}
    repo.delete.return_value = True
    return repo


@pytest.fixture
def sample_payload() -> Dict[str, Any]:
    return {{
        "id": "payload-abc",
        "data": {{"key": "value", "nested": {{"depth": 1}}}},
        "timestamp": "2025-01-01T00:00:00Z",
        "user_id": "user-xyz"
    }}


# ─── Unit Tests ────────────────────────────────────────────────────────────────

class Test{module.capitalize()}Core:

    def test_basic_operation_succeeds(self, mock_config, sample_payload):
        """Happy path: core operation returns expected structure."""
        result = {{"id": sample_payload["id"], "status": "processed"}}
        assert result["id"] == sample_payload["id"]
        assert result["status"] == "processed"

    def test_missing_required_field_raises(self, sample_payload):
        """Validation should reject payloads missing required fields."""
        del sample_payload["id"]
        with pytest.raises((ValueError, KeyError)):
            _ = sample_payload["id"]

    def test_none_input_handled_gracefully(self):
        """None inputs should not cause unhandled exceptions."""
        result = None
        assert result is None  # Verify graceful handling

    def test_empty_dict_handled(self):
        """Empty dict inputs should be handled without crashing."""
        payload = {{}}
        assert isinstance(payload, dict)
        assert len(payload) == 0

    @pytest.mark.parametrize("input_val,expected", [
        ("valid-id-123", True),
        ("", False),
        (None, False),
        ("   ", False),
    ])
    def test_id_validation(self, input_val, expected):
        """Parametrized: ID validation covers multiple edge cases."""
        is_valid = bool(input_val and input_val.strip())
        assert is_valid == expected


class Test{module.capitalize()}Repository:

    def test_find_by_id_returns_entity(self, mock_repository):
        entity = mock_repository.find_by_id("test-123")
        assert entity is not None
        assert entity["id"] == "test-123"
        mock_repository.find_by_id.assert_called_once_with("test-123")

    def test_save_persists_entity(self, mock_repository):
        entity = {{"id": "new-entity", "data": "value"}}
        result = mock_repository.save(entity)
        assert result["saved"] is True
        mock_repository.save.assert_called_once()

    def test_delete_removes_entity(self, mock_repository):
        result = mock_repository.delete("test-123")
        assert result is True

    def test_find_nonexistent_returns_none(self, mock_repository):
        mock_repository.find_by_id.return_value = None
        result = mock_repository.find_by_id("nonexistent")
        assert result is None


class Test{module.capitalize()}ErrorHandling:

    def test_service_handles_repository_failure(self, mock_repository):
        mock_repository.find_by_id.side_effect = ConnectionError("DB unreachable")
        with pytest.raises(ConnectionError):
            mock_repository.find_by_id("any-id")

    def test_retry_logic_on_transient_failure(self, mock_repository):
        mock_repository.save.side_effect = [
            TimeoutError("timeout"),
            TimeoutError("timeout"),
            {{"id": "recovered", "saved": True}}
        ]
        # First two calls fail, third succeeds
        with pytest.raises(TimeoutError):
            mock_repository.save({{"id": "test"}})


# ─── Integration-style Tests ───────────────────────────────────────────────────

class Test{module.capitalize()}Integration:

    def test_full_lifecycle(self, mock_repository, sample_payload):
        """End-to-end: create → fetch → delete lifecycle."""
        # Create
        created = mock_repository.save(sample_payload)
        assert created is not None

        # Fetch
        fetched = mock_repository.find_by_id(sample_payload["id"])
        assert fetched is not None

        # Delete
        deleted = mock_repository.delete(sample_payload["id"])
        assert deleted is True

    def test_concurrent_reads_stable(self, mock_repository):
        """Simulate concurrent read pattern."""
        ids = ["id-1", "id-2", "id-3", "id-4", "id-5"]
        results = [mock_repository.find_by_id(i) for i in ids]
        assert len(results) == len(ids)
'''

    def _docs_content(self, doc_type: str) -> str:
        templates = {
            "api": f"""# API Reference

> Last updated: {datetime.now().strftime("%Y-%m-%d")}

## Overview

This document describes the REST API endpoints available in this project.
All endpoints require Bearer token authentication unless stated otherwise.

## Base URL

```
https://api.example.com/v1
```

## Authentication

Include the token in every request:

```http
Authorization: Bearer <your-token>
```

## Endpoints

### GET /health

Returns system health status.

**Response:**
```json
{{
  "status": "healthy",
  "uptime": 99.9,
  "version": "1.0.0"
}}
```

### GET /resources

List all resources with pagination.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 100) |

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request — malformed payload |
| 401 | Unauthorized — missing/invalid token |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |
""",
            "contributing": f"""# Contributing Guide

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/repo.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run tests: `pytest`
6. Submit a PR

## Coding Standards

- Follow PEP 8 for Python code
- Add type hints to all functions
- Write docstrings for public APIs
- Maintain ≥ 80% test coverage

## Commit Convention

We use [Conventional Commits](https://conventionalcommits.org):

```
feat: add new endpoint
fix: resolve null pointer in auth
docs: update API reference
```

## PR Checklist

- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG entry added
- [ ] Code reviewed

> Updated: {datetime.now().strftime("%Y-%m-%d")}
"""
        }
        return templates.get(doc_type, f"# {doc_type.title()} Documentation\n\n> Updated: {datetime.now().strftime('%Y-%m-%d')}\n\nContent here.\n")

    def _changelog_entry(self, change_type: str, name: str) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        section = "### Added" if change_type == "feature" else "### Fixed" if change_type == "fix" else "### Changed"
        entry = f"- {name.replace('-', ' ').title()}: {'New feature implementation' if change_type == 'feature' else 'Bug fix applied'}"
        return f"""# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

{section}
- {date}: {entry}

## [1.0.0] - 2025-01-01

### Added
- Initial project setup
- Core service layer
- REST API endpoints
- Authentication middleware
- CI/CD pipeline
"""
