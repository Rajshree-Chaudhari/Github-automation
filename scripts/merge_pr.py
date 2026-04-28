#!/usr/bin/env python3
"""
Merge PR Script
Merges a specific PR number. Called by the auto-merge workflow.
(Approval step removed to avoid GitHub 422 errors)
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
def merge_pr(github: GitHubClient, pr_number: int):
    # Fetch PR details
    pr = github._request("GET", github._url(f"/pulls/{pr_number}"))

    state = pr.get("state")
    mergeable = pr.get("mergeable")
    mergeable_state = pr.get("mergeable_state")

    logger.info(f"PR #{pr_number} state: {state}")
    logger.info(f"PR #{pr_number} mergeable: {mergeable}")
    logger.info(f"PR #{pr_number} mergeable_state: {mergeable_state}")

    # Skip if already closed/merged
    if state != "open":
        logger.info(f"PR #{pr_number} is already {state} — skipping")
        return

    # GitHub sometimes returns mergeable=None initially → wait & retry
    if mergeable is None:
        logger.warning(f"PR #{pr_number} mergeable unknown — retrying...")
        time.sleep(10)
        raise Exception("Mergeable status not ready")

    # If not mergeable, retry
    if not mergeable or mergeable_state not in ["clean", "unstable"]:
        logger.warning(f"PR #{pr_number} not ready for merge — waiting")
        time.sleep(30)
        raise Exception(f"Not mergeable (state={mergeable_state})")

    # Simulate human delay before merge
    wait = random.randint(5, 15)
    logger.info(f"Waiting {wait}s before merge...")
    time.sleep(wait)

    # Merge
    merge_method = random.choice(["squash", "merge"])
    logger.info(f"Merging PR #{pr_number} via {merge_method}")

    result = github.merge_pull_request(pr_number, merge_method=merge_method)

    if not result.get("merged"):
        raise Exception(f"Merge failed: {result}")

    # Cleanup branch
    branch = pr.get("head", {}).get("ref")
    if branch:
        try:
            github.delete_branch(branch)
            logger.info(f"Branch {branch} deleted")
        except Exception as e:
            logger.warning(f"Failed to delete branch {branch}: {e}")

    logger.info(f"✅ PR #{pr_number} merged successfully")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()

    settings = Settings()
    github = GitHubClient(settings)

    try:
        merge_pr(github, args.pr_number)
    except Exception as e:
        logger.error(f"Merge failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()








##################################################################################################################################
# USE BELOW CODE IF YOU WANT APPROVAL PROCESS
##################################################################################################################################


# #!/usr/bin/env python3
# """
# Merge PR Script
# Approves and merges a specific PR number. Called by the auto-merge workflow.
# """

# import sys
# import time
# import random
# import argparse
# import logging
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent.parent))

# from config.settings import Settings
# from src.utils.github_client import GitHubClient
# from src.utils.retry import retry_with_backoff
# from src.utils.logger import setup_logger

# logger = setup_logger("merge_pr")


# @retry_with_backoff(max_retries=3, backoff_factor=2)
# def approve_and_merge(github: GitHubClient, pr_number: int):
#     # Check if PR is still open and mergeable
#     pr = github._request("GET", github._url(f"/pulls/{pr_number}"))

#     if pr.get("state") != "open":
#         logger.info(f"PR #{pr_number} is already {pr.get('state')} — skipping")
#         return

#     if not pr.get("mergeable", True):
#         logger.warning(f"PR #{pr_number} not currently mergeable — waiting for checks")
#         time.sleep(30)
#         raise Exception("PR not yet mergeable — will retry")

#     # Approve
#     logger.info(f"Approving PR #{pr_number}")
#     github.approve_pull_request(pr_number)
#     time.sleep(random.randint(5, 15))

#     # Merge
#     merge_method = random.choice(["squash", "merge"])
#     logger.info(f"Merging PR #{pr_number} via {merge_method}")
#     github.merge_pull_request(pr_number, merge_method=merge_method)

#     # Cleanup branch
#     branch = pr.get("head", {}).get("ref")
#     if branch:
#         github.delete_branch(branch)
#         logger.info(f"Branch {branch} deleted")

#     logger.info(f"PR #{pr_number} merged successfully")


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--pr-number", required=True, type=int)
#     args = parser.parse_args()

#     settings = Settings()
#     github = GitHubClient(settings)

#     try:
#         approve_and_merge(github, args.pr_number)
#     except Exception as e:
#         logger.error(f"Merge failed: {e}", exc_info=True)
#         sys.exit(1)


# if __name__ == "__main__":
#     main()
