#!/usr/bin/env python3
"""
Weekly Report Generator
Summarizes automation activity for the past 7 days.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings  # noqa: E402
from src.utils.github_client import GitHubClient  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

logger = setup_logger("weekly_report")


def generate_report(github: GitHubClient, settings: Settings) -> dict:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": "last_7_days",
        "repository": f"{settings.repo_owner}/{settings.repo_name}",
        "prs_created": 0,
        "prs_merged": 0,
        "commits": 0,
        "change_types": {},
    }

    try:
        pulls = github._request(
            "GET", github._url("/pulls?state=all&per_page=100&sort=created&direction=desc")
        )
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        for pr in pulls:
            created_at_str = pr.get("created_at", "")
            if not created_at_str:
                continue
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            if created_at < week_ago:
                break

            report["prs_created"] += 1
            if pr.get("merged_at"):
                report["prs_merged"] += 1

            branch = pr.get("head", {}).get("ref", "")
            for prefix in ["feature", "fix", "refactor", "docs", "perf", "test"]:
                if branch.startswith(f"{prefix}/"):
                    report["change_types"][prefix] = report["change_types"].get(prefix, 0) + 1
                    break

    except Exception as e:
        logger.warning(f"Could not fetch PRs: {e}")

    return report


def main():
    settings = Settings()
    github = GitHubClient(settings)

    report = generate_report(github, settings)
    Path("reports").mkdir(exist_ok=True)

    report_path = Path("reports") / f"weekly_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Weekly report saved: {report_path}")
    logger.info(f"Summary: {report['prs_created']} PRs created, {report['prs_merged']} merged")


if __name__ == "__main__":
    main()
