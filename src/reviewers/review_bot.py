#!/usr/bin/env python3
"""
Review Bot
Generates professional, context-aware PR review comments.
Simulates senior engineer review patterns.
"""

import random
import time
import logging
from datetime import datetime
from typing import Optional
from config.settings import Settings
from src.utils.github_client import GitHubClient

logger = logging.getLogger("review_bot")


# ─── Review Comment Templates ─────────────────────────────────────────────────

INLINE_COMMENTS = {
    "positive": [
        "Nice clean implementation. The separation of concerns here is clear.",
        "Good use of type hints — makes the intent explicit.",
        "Smart use of the guard clause pattern here. Keeps the happy path readable.",
        "Appreciate the docstring — this will help future contributors.",
        "Well-structured error handling. The specific exception types are helpful.",
        "Clean dataclass usage. Much better than a raw dict here.",
        "Good logging placement — this will be invaluable during debugging.",
        "Solid use of `@functools.wraps` — preserves metadata correctly.",
    ],
    "suggestions": [
        "Consider extracting this into a private helper method to reduce nesting.",
        "This could be memoized if called frequently with the same arguments.",
        "Minor: the variable name `d` could be more descriptive — maybe `entity_data`?",
        "Consider adding a `__repr__` for easier debugging in logs.",
        "Worth adding a note here about why this specific timeout value was chosen.",
        "Nit: trailing whitespace on this line.",
        "Could we add a `TODO` here to track the planned optimization?",
        "Consider using `dataclasses.field(default_factory=...)` to avoid mutable defaults.",
    ],
    "questions": [
        "Wondering — should we also handle the case where `data` is an empty list?",
        "Is there a reason we're using `time.time()` rather than `time.monotonic()` here?",
        "Should this raise or silently return `None` on invalid input? Worth documenting.",
        "Is this the right abstraction boundary? Open to thoughts on the team call.",
        "Will this work correctly under concurrent access, or do we need a lock here?",
    ],
}

REVIEW_SUMMARIES = {
    "feature": [
        "Solid implementation overall. The service layer is well-structured and the error handling is thoughtful. Left a few minor suggestions inline — nothing blocking.",
        "Good work on this feature. The API endpoints follow our existing conventions nicely. A couple of nits below, but happy to approve once those are addressed.",
        "This is a clean addition. Tests cover the happy path well — we may want to add more edge case coverage in a follow-up, but that shouldn't block this PR.",
    ],
    "fix": [
        "The root cause analysis is thorough and the fix is appropriately scoped. Good that we have a regression test now. LGTM.",
        "Targeted fix — exactly what's needed. The guard clause approach is the right call here. Regression test is well-placed.",
        "Clean fix with proper test coverage. Appreciate that we're not over-engineering the solution. Approving.",
    ],
    "refactor": [
        "Nice cleanup. The abstraction boundaries are clearer now and the dependency injection makes this much more testable. No functional changes confirmed.",
        "Good refactor — the Protocol-based approach gives us flexibility to swap implementations easily. Existing tests still passing is the key signal here.",
        "Clean structural improvement. The code reads more clearly and the single-responsibility principle is much better respected. LGTM.",
    ],
    "docs": [
        "Documentation is clear and accurate. The examples are helpful additions. LGTM.",
        "Good update — the API table is particularly useful for new consumers. Minor formatting note below.",
    ],
    "perf": [
        "Impressive benchmark improvement. The LRU cache implementation is clean and the TTL logic is correct. Load test results are convincing. Approving.",
        "The batch processor approach makes sense for this use case. The performance numbers speak for themselves. Good work.",
    ],
    "test": [
        "Good test additions. The parametrized tests cover the edge cases well. Coverage improvement is meaningful. LGTM.",
        "Solid test structure — the fixture setup is clean and the integration tests add real confidence. Approving.",
    ],
}

ACTION_ITEMS = [
    "Let's circle back on the caching strategy in the next sprint if we see performance issues.",
    "Worth filing a separate ticket to track the `TODO` we added — don't want it to get lost.",
    "If we revisit this module, we should consider adding OpenTelemetry spans here.",
    "Low priority: we could batch these calls for better efficiency when volume grows.",
]


class ReviewBot:
    def __init__(self, settings: Settings, github: GitHubClient):
        self.settings = settings
        self.github = github
        self.reviewer_name = settings.reviewer_name

    def review_pr(self, pr_number: int, change_type: str, changes: list):
        """Perform a full automated review: inline comments + summary review."""
        logger.info(f"Starting review for PR #{pr_number} (type: {change_type})")

        # Step 1: Post an initial "looking into this" comment (optional, realistic)
        if random.random() > 0.6:
            self._post_initial_comment(pr_number)
            time.sleep(random.randint(15, 45))

        # Step 2: Fetch PR files for context
        try:
            pr_files = self.github.get_pr_files(pr_number)
        except Exception as e:
            logger.warning(f"Could not fetch PR files: {e}")
            pr_files = []

        # Step 3: Generate inline review comments
        inline_comments = self._generate_inline_comments(pr_files, change_type)

        # Step 4: Generate the overall review summary
        summary = self._generate_summary(change_type, len(inline_comments))

        # Step 5: Submit the review
        try:
            self.github.create_review(
                pr_number=pr_number,
                body=summary,
                event="COMMENT",      # First pass: comment only
                comments=inline_comments[:3] if inline_comments else []  # Max 3 inline
            )
            logger.info(f"Review submitted for PR #{pr_number}")
        except Exception as e:
            logger.error(f"Failed to submit review: {e}")
            # Fallback: at least post the summary as a comment
            try:
                self.github.add_pr_comment(pr_number, summary)
            except Exception as e2:
                logger.error(f"Fallback comment also failed: {e2}")

    def _post_initial_comment(self, pr_number: int):
        openers = [
            "Taking a look at this now 👀",
            "Reviewing — back shortly with feedback.",
            "On it! Will post comments shortly.",
            "Good timing — reviewing this now.",
        ]
        try:
            self.github.add_pr_comment(pr_number, random.choice(openers))
        except Exception as e:
            logger.warning(f"Could not post opener comment: {e}")

    def _generate_inline_comments(self, pr_files: list, change_type: str) -> list:
        """Generate position-based inline comments on changed files."""
        comments: list[dict] = []

        if not pr_files:
            return comments

        # Pick 1-3 files to comment on
        files_to_comment = random.sample(pr_files, min(len(pr_files), random.randint(1, 3)))

        for file_info in files_to_comment:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")

            if not patch:
                continue

            # Find a valid position in the patch
            lines = patch.split("\n")
            valid_positions = [i + 1 for i, line in enumerate(lines) if line.startswith("+") and not line.startswith("+++")]

            if not valid_positions:
                continue

            position = random.choice(valid_positions)
            comment_body = self._pick_comment(change_type, filename)

            comments.append({
                "path": filename,
                "position": position,
                "body": comment_body
            })

        return comments

    def _pick_comment(self, change_type: str, filename: str) -> str:
        # Weight: 40% positive, 40% suggestion, 20% question
        category = random.choices(
            ["positive", "suggestions", "questions"],
            weights=[40, 40, 20]
        )[0]

        comment = random.choice(INLINE_COMMENTS[category])

        # Add file-specific context occasionally
        if random.random() > 0.7 and filename:
            ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext == "py":
                comment += " " + random.choice([
                    "Might also want to add a `py.typed` marker if this becomes a library.",
                    "Consider using `__slots__` here if this class is instantiated heavily.",
                ])

        return comment

    def _generate_summary(self, change_type: str, comment_count: int) -> str:
        templates = REVIEW_SUMMARIES.get(change_type, REVIEW_SUMMARIES["feature"])
        summary = random.choice(templates)

        parts = [f"**Code Review — {datetime.now().strftime('%Y-%m-%d')}**\n"]
        parts.append(summary)

        if comment_count > 0:
            parts.append(f"\nLeft {comment_count} inline comment{'s' if comment_count > 1 else ''} — see individual notes above.")

        if random.random() > 0.6:
            parts.append(f"\n> 💡 {random.choice(ACTION_ITEMS)}")

        return "\n".join(parts)
