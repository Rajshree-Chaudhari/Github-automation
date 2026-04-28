#!/usr/bin/env python3
"""
Post Review Script
Called by the auto-review workflow to submit a review on a specific PR.
"""

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.utils.github_client import GitHubClient
from src.reviewers.review_bot import ReviewBot
from src.utils.logger import setup_logger

logger = setup_logger("post_review")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()

    settings = Settings()
    github = GitHubClient(settings)
    bot = ReviewBot(settings, github)

    logger.info(f"Posting review on PR #{args.pr_number}")

    # Determine change type from branch name
    try:
        pr = github._request("GET", github._url(f"/pulls/{args.pr_number}"))
        branch = pr.get("head", {}).get("ref", "")
        change_type = branch.split("/")[0] if "/" in branch else "feature"
        change_type = change_type if change_type in ["feature", "fix", "refactor", "docs", "perf", "test"] else "feature"

        files = github.get_pr_files(args.pr_number)
        bot.review_pr(args.pr_number, change_type, [{"path": f["filename"]} for f in files])
        logger.info("Review posted successfully")
    except Exception as e:
        logger.error(f"Failed to post review: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
