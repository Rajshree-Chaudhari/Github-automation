#!/usr/bin/env python3
"""Cleanup script for failed automation runs."""

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from src.utils.github_client import GitHubClient
from src.utils.logger import setup_logger

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
                # Close the PR first
                github._request("PATCH", github._url(f"/pulls/{args.pr_number}"),
                               json={"state": "closed"})
                logger.info(f"Closed PR #{args.pr_number}")
            if branch:
                github.delete_branch(branch)
                logger.info(f"Deleted branch: {branch}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
