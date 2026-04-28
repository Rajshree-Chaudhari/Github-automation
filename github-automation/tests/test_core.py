#!/usr/bin/env python3
"""
Test Suite for DevFlow Automator Core Components
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.code_generator import CodeGenerator, CHANGE_WEIGHTS
from src.generators.pr_generator import PRGenerator
from src.utils.retry import retry_with_backoff


# ─── Fixtures ──────────────────────────────────────────────────────────────────

class MockSettings:
    github_token = "test-token"
    repo_owner = "test-owner"
    repo_name = "test-repo"
    project_name = "test-project"
    reviewer_name = "test-reviewer"
    default_branch = "main"
    max_delay_seconds = 0
    dry_run = True


@pytest.fixture
def settings():
    return MockSettings()


@pytest.fixture
def code_gen(settings):
    return CodeGenerator(settings)


@pytest.fixture
def pr_gen(settings):
    return PRGenerator(settings)


# ─── CodeGenerator Tests ───────────────────────────────────────────────────────

class TestCodeGenerator:

    def test_select_change_type_returns_valid(self, code_gen):
        for _ in range(20):
            ct = code_gen.select_change_type()
            assert ct in CHANGE_WEIGHTS

    def test_branch_name_feature_prefix(self, code_gen):
        branch = code_gen.generate_branch_name("feature")
        assert branch.startswith("feature/")

    def test_branch_name_fix_prefix(self, code_gen):
        branch = code_gen.generate_branch_name("fix")
        assert branch.startswith("fix/")

    def test_branch_name_refactor_prefix(self, code_gen):
        branch = code_gen.generate_branch_name("refactor")
        assert branch.startswith("refactor/")

    def test_commit_message_conventional_format(self, code_gen):
        change = {"path": "src/test.py", "description": "test module"}
        msg = code_gen.generate_commit_message("feature", change)
        assert msg.startswith("feat")

    def test_generate_changes_returns_list(self, code_gen):
        for ct in CHANGE_WEIGHTS.keys():
            changes = code_gen.generate_changes(ct)
            assert isinstance(changes, list)
            assert len(changes) >= 1

    def test_changes_have_required_keys(self, code_gen):
        changes = code_gen.generate_changes("feature")
        for change in changes:
            assert "path" in change
            assert "content" in change

    def test_content_is_non_empty_string(self, code_gen):
        changes = code_gen.generate_changes("feature")
        for change in changes:
            assert isinstance(change["content"], str)
            assert len(change["content"]) > 50


# ─── PRGenerator Tests ─────────────────────────────────────────────────────────

class TestPRGenerator:

    def test_generate_pr_returns_required_keys(self, pr_gen):
        changes = [{"path": "src/test.py", "description": "test", "scope": "core"}]
        result = pr_gen.generate_pr("feature", changes, "feature/test-0101")
        assert "title" in result
        assert "body" in result
        assert "labels" in result

    def test_title_not_empty(self, pr_gen):
        changes = [{"path": "src/test.py", "description": "test module", "scope": "api"}]
        result = pr_gen.generate_pr("fix", changes, "fix/null-ptr-0101")
        assert len(result["title"]) > 5

    def test_body_contains_summary_section(self, pr_gen):
        changes = [{"path": "src/test.py", "description": "test", "scope": "core"}]
        result = pr_gen.generate_pr("feature", changes, "feature/search-0101")
        assert "##" in result["body"]

    def test_labels_are_list(self, pr_gen):
        changes = [{"path": "src/test.py", "description": "test", "scope": "core"}]
        result = pr_gen.generate_pr("feature", changes, "feature/x-0101")
        assert isinstance(result["labels"], list)

    @pytest.mark.parametrize("change_type", ["feature", "fix", "refactor", "docs", "perf", "test"])
    def test_all_change_types_generate_pr(self, pr_gen, change_type):
        changes = [{"path": "src/test.py", "description": "test", "scope": "core"}]
        result = pr_gen.generate_pr(change_type, changes, f"{change_type}/test-0101")
        assert result["title"]
        assert result["body"]


# ─── Retry Decorator Tests ─────────────────────────────────────────────────────

class TestRetryDecorator:

    def test_succeeds_on_first_try(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0.01)
        def func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = func()
        assert result == "success"
        assert call_count == 1

    def test_retries_on_failure_then_succeeds(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0.01)
        def func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient error")
            return "recovered"

        result = func()
        assert result == "recovered"
        assert call_count == 3

    def test_raises_after_max_retries(self):
        @retry_with_backoff(max_retries=2, backoff_factor=0.01)
        def func():
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError):
            func()

    def test_only_catches_specified_exceptions(self):
        @retry_with_backoff(max_retries=3, backoff_factor=0.01, exceptions=(ValueError,))
        def func():
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            func()
