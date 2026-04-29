#!/usr/bin/env python3
"""Cleanup script for failed automation runs."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings  # noqa: E402
from src.utils.github_client import GitHubClient  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

logger = setup_logger("cleanup")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-number", type=int)
    args = parser.parse_args()

    settings = Settings()
    github = GitHubClient(settings)

    if args.pr_number:
        try:
            pr = github._request("GET", github._url(f"/pulls/{args.pr_number}"))
            branch = pr.get("head", {}).get("ref")
            if branch and pr.get("state") == "open":
                github._request(
                    "PATCH",
                    github._url(f"/pulls/{args.pr_number}"),
                    json={"state": "closed"},
                )
                logger.info(f"Closed PR #{args.pr_number}")
            if branch:
                github.delete_branch(branch)
                logger.info(f"Deleted branch: {branch}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
