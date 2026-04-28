#!/usr/bin/env python3
"""
PR Generator
Produces professional, realistic PR titles and descriptions.
"""

import random
import logging
from datetime import datetime
from typing import Optional
from config.settings import Settings

logger = logging.getLogger("pr_generator")

PR_TEMPLATES = {
    "feature": {
        "titles": [
            "feat({scope}): implement {name} with full test coverage",
            "feat: add {name} service and REST API endpoints",
            "feat({scope}): introduce {name} — closes #{ticket}",
            "feat: {name} — initial implementation",
        ],
        "labels": ["enhancement", "feature"],
        "reviewers_note": "This is a new feature addition.",
    },
    "fix": {
        "titles": [
            "fix({scope}): resolve {name} edge case",
            "fix: patch {name} — fixes #{ticket}",
            "fix({scope}): handle {name} in production scenarios",
            "hotfix: critical {name} regression",
        ],
        "labels": ["bug", "fix"],
        "reviewers_note": "This is a targeted bug fix.",
    },
    "refactor": {
        "titles": [
            "refactor({scope}): {name}",
            "refactor: clean up {name} for better maintainability",
            "refactor({scope}): decouple {name} from core module",
        ],
        "labels": ["refactor", "tech-debt"],
        "reviewers_note": "No functional changes — internal structure only.",
    },
    "docs": {
        "titles": [
            "docs: update {name} documentation",
            "docs({scope}): expand {name} with examples",
            "docs: improve {name} clarity and accuracy",
        ],
        "labels": ["documentation"],
        "reviewers_note": "Documentation update only.",
    },
    "perf": {
        "titles": [
            "perf({scope}): optimize {name} — 3x throughput improvement",
            "perf: reduce {name} latency with caching layer",
            "perf({scope}): batch {name} operations for efficiency",
        ],
        "labels": ["performance"],
        "reviewers_note": "Performance improvement — benchmark results attached.",
    },
    "test": {
        "titles": [
            "test({scope}): add unit tests for {name}",
            "test: expand {name} coverage to 90%+",
            "test({scope}): cover edge cases in {name}",
        ],
        "labels": ["testing"],
        "reviewers_note": "Test coverage improvement.",
    },
}

PR_BODY_SECTIONS = {
    "feature": """## 🚀 Summary

{summary}

## 🎯 Motivation

{motivation}

## 📋 Changes Made

{changes_list}

## 🧪 Testing

- [x] Unit tests added
- [x] Integration tests pass
- [x] Manual smoke test performed
- [ ] Load tested (N/A for this scope)

## 📸 Screenshots / Evidence

> N/A — backend change only

## ⚠️ Breaking Changes

None. This is a purely additive change.

## 🔗 Related Issues

{related}

## 📝 Checklist

- [x] Code follows project style guide
- [x] Self-reviewed the diff
- [x] Tests cover happy path and edge cases
- [x] Documentation updated where applicable
- [x] CHANGELOG entry added
""",
    "fix": """## 🐛 Bug Description

{summary}

## 🔍 Root Cause

{motivation}

## 🔧 Fix Applied

{changes_list}

## 🧪 Reproduction Steps (Before Fix)

1. Trigger the specific edge case
2. Observe the error / unexpected behavior

## ✅ Verification (After Fix)

1. Same steps no longer reproduce the issue
2. Regression tests added to prevent recurrence

## 🔗 Related Issues

{related}

## ⚠️ Risk Assessment

**Low** — targeted fix with no side effects on adjacent modules.

## 📝 Checklist

- [x] Root cause identified and documented
- [x] Regression test added
- [x] No unintended side effects
- [x] CHANGELOG entry added
""",
    "refactor": """## ♻️ Summary

{summary}

## 💡 Motivation

{motivation}

## 📋 Changes

{changes_list}

## ✅ No Functional Changes

This PR contains zero behavior changes. All existing tests pass without modification.

## 🧪 Validation

- [x] All existing tests pass
- [x] No public API changes
- [x] Dependency graph unchanged

## 📝 Checklist

- [x] Purely structural changes
- [x] Tests still green
- [x] No performance regressions
""",
    "docs": """## 📖 Documentation Update

{summary}

## 📋 What Changed

{changes_list}

## ✅ Checklist

- [x] Spelling and grammar checked
- [x] Code examples are accurate and tested
- [x] Links verified
""",
    "perf": """## ⚡ Performance Improvement

{summary}

## 📊 Benchmark Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| p50    | ~450ms | ~80ms | 5.6x faster |
| p95    | ~1.2s  | ~210ms| 5.7x faster |
| p99    | ~2.8s  | ~450ms| 6.2x faster |
| Memory | 380MB  | 195MB | 49% reduced |

## 🔧 Optimization Strategy

{changes_list}

## 🧪 Testing

- [x] Benchmarks run in isolated environment
- [x] No regression in correctness
- [x] Load test confirms improvements hold under traffic

## ⚠️ Risk

**Low** — optimization is isolated to internal implementation.
""",
    "test": """## 🧪 Test Coverage Improvement

{summary}

## 📊 Coverage Report

| Module | Before | After |
|--------|--------|-------|
| Core   | 72%    | 91%   |
| Utils  | 65%    | 88%   |
| API    | 80%    | 95%   |

## 📋 Tests Added

{changes_list}

## ✅ Checklist

- [x] All new tests pass
- [x] No existing tests broken
- [x] Edge cases covered
""",
}

SUMMARIES = {
    "feature": [
        "Introduces the {name} module as part of the ongoing platform expansion initiative.",
        "Adds full implementation of {name} including service layer, API endpoints, and validation.",
        "Implements {name} functionality to support upcoming product requirements.",
    ],
    "fix": [
        "Resolves a reported issue in {name} where edge-case inputs caused unexpected behavior.",
        "Patches a regression in {name} introduced in a recent deployment.",
        "Fixes {name} handling to properly manage boundary conditions and null states.",
    ],
    "refactor": [
        "Restructures the {name} module to improve readability and reduce coupling.",
        "Extracts reusable logic from {name} into a dedicated, testable utility class.",
        "Simplifies {name} by removing dead code paths and introducing cleaner abstractions.",
    ],
    "docs": ["Updates documentation for {name} to reflect recent API changes and add usage examples."],
    "perf": ["Optimizes {name} operations to reduce latency and improve throughput under load."],
    "test": ["Adds comprehensive test coverage for {name} targeting edge cases and error paths."],
}

MOTIVATIONS = {
    "feature": [
        "This feature was prioritized in our Q{quarter} roadmap to address growing user demand.",
        "Product team requested this capability to unblock the {name} integration milestone.",
        "Identified gap in functionality during the platform audit — added proactively.",
    ],
    "fix": [
        "This bug was surfaced during QA regression testing and needed to be addressed before the next release.",
        "Production monitoring flagged unexpected error rates in this code path.",
        "Reported by internal stakeholders during UAT — reproduced reliably in staging.",
    ],
    "refactor": [
        "Technical debt accumulated in this module was impacting development velocity.",
        "Preparing the codebase for the upcoming {name} scaling requirements.",
        "Code review feedback from the team highlighted maintainability concerns.",
    ],
    "docs": ["API consumers flagged missing documentation during integration."],
    "perf": ["Profiling identified this as a hotspot contributing to P99 latency degradation."],
    "test": ["Coverage report showed this module as undertested — addressed proactively."],
}


class PRGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_pr(self, change_type: str, changes: list, branch_name: str) -> dict:
        template = PR_TEMPLATES.get(change_type, PR_TEMPLATES["feature"])
        name = self._extract_name(changes, branch_name)
        scope = changes[0].get("scope", "core") if changes else "core"
        ticket = random.randint(100, 999)
        quarter = ((datetime.now().month - 1) // 3) + 1

        title_template = random.choice(template["titles"])
        title = title_template.format(name=name, scope=scope, ticket=ticket)

        summary_template = random.choice(SUMMARIES.get(change_type, SUMMARIES["feature"]))
        summary = summary_template.format(name=name, quarter=quarter)

        motivation_template = random.choice(MOTIVATIONS.get(change_type, MOTIVATIONS["feature"]))
        motivation = motivation_template.format(name=name, quarter=quarter)

        changes_list = self._format_changes_list(changes)
        related = f"- Relates to #{random.randint(50, 300)}" if random.random() > 0.4 else "- N/A"

        body_template = PR_BODY_SECTIONS.get(change_type, PR_BODY_SECTIONS["feature"])
        body = body_template.format(
            summary=summary,
            motivation=motivation,
            changes_list=changes_list,
            related=related
        )

        body += f"\n\n---\n*Auto-generated workflow run — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n"

        return {
            "title": title,
            "body": body,
            "labels": template["labels"],
        }

    def _extract_name(self, changes: list, branch_name: str) -> str:
        if changes:
            desc = changes[0].get("description", "")
            if desc:
                return desc.split(" ")[0]
        # Fallback: extract from branch name
        parts = branch_name.split("/")
        if len(parts) > 1:
            name_part = parts[1].rsplit("-", 1)[0]
            return name_part
        return "core module"

    def _format_changes_list(self, changes: list) -> str:
        lines = []
        for change in changes:
            path = change.get("path", "unknown")
            desc = change.get("description", "updated")
            lines.append(f"- `{path}` — {desc}")
        return "\n".join(lines) if lines else "- No specific files listed"
