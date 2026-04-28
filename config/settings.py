#!/usr/bin/env python3
"""
Settings
Centralizes all configuration. Reads from environment variables.
"""

import os
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("settings")


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required environment variable not set: {key}")
    return value


@dataclass
class Settings:
    # GitHub credentials
    github_token: str = field(default_factory=lambda: _require_env("GITHUB_TOKEN"))
    repo_owner: str = field(default_factory=lambda: _require_env("REPO_OWNER"))
    repo_name: str = field(default_factory=lambda: _require_env("REPO_NAME"))

    # Project metadata
    project_name: str = field(default_factory=lambda: os.getenv("PROJECT_NAME", "devflow-automator"))
    reviewer_name: str = field(default_factory=lambda: os.getenv("REVIEWER_NAME", "auto-reviewer"))
    default_branch: str = field(default_factory=lambda: os.getenv("DEFAULT_BRANCH", "main"))

    # Behavior config
    max_delay_seconds: int = field(default_factory=lambda: int(os.getenv("MAX_DELAY_SECONDS", "3600")))
    dry_run: bool = field(default_factory=lambda: os.getenv("DRY_RUN", "false").lower() == "true")

    def validate(self):
        assert self.github_token, "GITHUB_TOKEN is required"
        assert self.repo_owner, "REPO_OWNER is required"
        assert self.repo_name, "REPO_NAME is required"
        logger.info(f"Settings validated: {self.repo_owner}/{self.repo_name}")
        return self
