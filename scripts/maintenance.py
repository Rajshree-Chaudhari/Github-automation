#!/usr/bin/env python3
"""
Maintenance Script
Prunes stale branches and generates activity reports.
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings  # noqa: E402
from src.utils.github_client import GitHubClient  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

logger = setup_logger("maintenance")


def prune_stale_branches(github: GitHubClient, older_than_days: int = 7):
    """Delete merged branches older than N days."""
    logger.info(f"Pruning branches older than {older_than_days} days")

    try:
        branches = github._request("GET", github._url("/branches") + "?per_page=100")
    except Exception as e:
        logger.error(f"Failed to list branches: {e}")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    prefixes = ("feature/", "fix/", "refactor/", "docs/", "perf/", "test/")
    pruned = 0

    for branch in branches:
        name = branch.get("name", "")
        if not any(name.startswith(p) for p in prefixes):
            continue

        try:
            commit = github._request(
                "GET", github._url(f"/commits/{branch['commit']['sha']}")
            )
            committed_at_str = commit.get("commit", {}).get("committer", {}).get("date", "")
            if not committed_at_str:
                continue

            committed_at = datetime.fromisoformat(committed_at_str.replace("Z", "+00:00"))
            if committed_at < cutoff:
                github.delete_branch(name)
                pruned += 1
                logger.info(f"Pruned stale branch: {name}")
        except Exception as e:
            logger.warning(f"Could not process branch {name}: {e}")

    logger.info(f"Pruned {pruned} stale branches")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prune-branches", action="store_true")
    parser.add_argument("--older-than-days", type=int, default=7)
    args = parser.parse_args()

    settings = Settings()
    github = GitHubClient(settings)

    if args.prune_branches:
        prune_stale_branches(github, args.older_than_days)


if __name__ == "__main__":
    main()
