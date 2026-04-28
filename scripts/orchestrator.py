#!/usr/bin/env python3
"""
DevFlow Automator - Main Orchestrator
Coordinates the full PR lifecycle: branch → changes → PR → review → merge
"""

import os
import sys
import time
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.code_generator import CodeGenerator
from src.generators.pr_generator import PRGenerator
from src.reviewers.review_bot import ReviewBot
from src.utils.github_client import GitHubClient
from src.utils.logger import setup_logger
from src.utils.retry import retry_with_backoff
from config.settings import Settings

logger = setup_logger("orchestrator")


def parse_args():
    parser = argparse.ArgumentParser(description="DevFlow Automator Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making real changes")
    parser.add_argument("--delay", type=int, default=0, help="Initial delay in seconds (for randomized scheduling)")
    parser.add_argument("--change-type", choices=["feature", "fix", "refactor", "docs", "perf", "test"], help="Force a specific change type")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()


def apply_random_delay(max_delay: int = 3600):
    """Apply a random delay to simulate organic commit timing."""
    if max_delay > 0:
        delay = random.randint(0, max_delay)
        logger.info(f"Applying organic delay: {delay}s before execution")
        time.sleep(delay)


class DevFlowOrchestrator:
    def __init__(self, settings: Settings, dry_run: bool = False):
        self.settings = settings
        self.dry_run = dry_run
        self.github = GitHubClient(settings)
        self.code_gen = CodeGenerator(settings)
        self.pr_gen = PRGenerator(settings)
        self.review_bot = ReviewBot(settings, self.github)

        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.branch_name = None
        self.pr_number = None

    def run(self, change_type: str = None) -> bool:
        logger.info(f"=== DevFlow Automator Run ID: {self.run_id} ===")
        logger.info(f"Dry run: {self.dry_run}")

        try:
            # Step 1: Select change type
            change_type = change_type or self.code_gen.select_change_type()
            logger.info(f"Selected change type: {change_type}")

            # Step 2: Generate branch name
            self.branch_name = self.code_gen.generate_branch_name(change_type)
            logger.info(f"Branch name: {self.branch_name}")

            # Step 3: Generate code changes
            changes = self.code_gen.generate_changes(change_type)
            logger.info(f"Generated {len(changes)} file change(s)")

            # Step 4: Create branch and commit changes
            if not self.dry_run:
                self._create_branch_and_commit(changes, change_type)

            # Step 5: Create Pull Request
            pr_data = self.pr_gen.generate_pr(change_type, changes, self.branch_name)
            if not self.dry_run:
                self.pr_number = self._create_pull_request(pr_data)
                logger.info(f"PR #{self.pr_number} created successfully")

            # Step 6: Automated review
            time.sleep(random.randint(30, 120))  # Simulate review think time
            if not self.dry_run and self.pr_number:
                self._perform_review(change_type, changes)

            # Step 7: Approve and merge
            time.sleep(random.randint(60, 300))  # Simulate approval delay
            if not self.dry_run and self.pr_number:
                self._approve_and_merge()

            logger.info(f"=== Run {self.run_id} completed successfully ===")
            return True

        except Exception as e:
            logger.error(f"Orchestrator failed: {e}", exc_info=True)
            self._handle_failure(e)
            return False

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def _create_branch_and_commit(self, changes: list, change_type: str):
        logger.info(f"Creating branch: {self.branch_name}")
        base_sha = self.github.get_branch_sha(self.settings.default_branch)
        self.github.create_branch(self.branch_name, base_sha)

        for change in changes:
            commit_message = self.code_gen.generate_commit_message(change_type, change)
            self.github.commit_file(
                branch=self.branch_name,
                path=change["path"],
                content=change["content"],
                message=commit_message,
                existing_sha=change.get("existing_sha")
            )
            logger.info(f"Committed: {change['path']}")
            time.sleep(random.uniform(0.5, 2.0))  # Rate limit safety

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def _create_pull_request(self, pr_data: dict) -> int:
        pr = self.github.create_pull_request(
            title=pr_data["title"],
            body=pr_data["body"],
            head=self.branch_name,
            base=self.settings.default_branch,
            labels=pr_data.get("labels", [])
        )
        return pr["number"]

    @retry_with_backoff(max_retries=2, backoff_factor=3)
    def _perform_review(self, change_type: str, changes: list):
        logger.info(f"Performing review on PR #{self.pr_number}")
        self.review_bot.review_pr(self.pr_number, change_type, changes)

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def _approve_and_merge(self):
        logger.info(f"Approving PR #{self.pr_number}")

        # Check merge conditions
        if not self.github.is_pr_mergeable(self.pr_number):
            logger.warning("PR not mergeable, waiting for checks...")
            time.sleep(60)

        # Approve the PR
        self.github.approve_pull_request(self.pr_number)
        time.sleep(random.randint(10, 30))

        # Merge the PR
        merge_method = random.choice(["squash", "merge"])  # Vary merge methods
        self.github.merge_pull_request(
            pr_number=self.pr_number,
            merge_method=merge_method,
            commit_title=f"Merge PR #{self.pr_number}"
        )
        logger.info(f"PR #{self.pr_number} merged via {merge_method}")

        # Cleanup branch
        self.github.delete_branch(self.branch_name)
        logger.info(f"Branch {self.branch_name} deleted")

    def _handle_failure(self, error: Exception):
        logger.error(f"Failure in run {self.run_id}: {error}")
        # Attempt to cleanup orphan branch
        if self.branch_name and not self.dry_run:
            try:
                self.github.delete_branch(self.branch_name)
                logger.info(f"Cleaned up branch: {self.branch_name}")
            except Exception:
                pass


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Apply randomized delay for organic scheduling
    if args.delay > 0:
        apply_random_delay(args.delay)

    settings = Settings()
    orchestrator = DevFlowOrchestrator(settings, dry_run=args.dry_run)
    success = orchestrator.run(change_type=args.change_type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
