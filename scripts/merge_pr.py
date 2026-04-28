#!/usr/bin/env python3
"""
Merge PR Script
Approves and merges a specific PR number. Called by the auto-merge workflow.
"""

import sys
import time
import random
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.utils.github_client import GitHubClient
from src.utils.retry import retry_with_backoff
from src.utils.logger import setup_logger

logger = setup_logger("merge_pr")


@retry_with_backoff(max_retries=3, backoff_factor=2)
def approve_and_merge(github: GitHubClient, pr_number: int):
    # Check if PR is still open and mergeable
    pr = github._request("GET", github._url(f"/pulls/{pr_number}"))

    if pr.get("state") != "open":
        logger.info(f"PR #{pr_number} is already {pr.get('state')} — skipping")
        return

    if not pr.get("mergeable", True):
        logger.warning(f"PR #{pr_number} not currently mergeable — waiting for checks")
        time.sleep(30)
        raise Exception("PR not yet mergeable — will retry")

    # Approve
    logger.info(f"Approving PR #{pr_number}")
    github.approve_pull_request(pr_number)
    time.sleep(random.randint(5, 15))

    # Merge
    merge_method = random.choice(["squash", "merge"])
    logger.info(f"Merging PR #{pr_number} via {merge_method}")
    github.merge_pull_request(pr_number, merge_method=merge_method)

    # Cleanup branch
    branch = pr.get("head", {}).get("ref")
    if branch:
        github.delete_branch(branch)
        logger.info(f"Branch {branch} deleted")

    logger.info(f"PR #{pr_number} merged successfully")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()

    settings = Settings()
    github = GitHubClient(settings)

    try:
        approve_and_merge(github, args.pr_number)
    except Exception as e:
        logger.error(f"Merge failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
