# 🤖 DevFlow Automator

> **Production-grade GitHub workflow automation** — automated PRs, reviews, and merges with organic scheduling and realistic commit patterns.

[![Daily Automation](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/YOUR_REPO/daily-automation.yml?label=Daily%20Automation&style=flat-square)](../../actions)
[![Auto Merge](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/YOUR_REPO/auto-merge.yml?label=Auto%20Merge&style=flat-square)](../../actions)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Workflow Details](#workflow-details)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## Overview

DevFlow Automator is a **fully automated GitHub activity system** that simulates realistic day-to-day development work. It creates meaningful PRs, performs code reviews, approves, and merges — all on a randomized schedule to maintain authentic contribution patterns.

**Built for:**
- Maintaining an active GitHub contribution graph
- Demonstrating CI/CD and automation skills
- Serving as a portfolio-grade DevOps project
- Learning GitHub Actions, REST API, and workflow orchestration

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│               GitHub Actions Scheduler               │
│         (Cron: Mon–Sat, varied UTC times)            │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│                  Orchestrator                        │
│   select_type → branch → generate → commit → PR     │
└───────┬───────────────┬──────────────────┬──────────┘
        │               │                  │
        ▼               ▼                  ▼
┌──────────────┐ ┌─────────────┐  ┌───────────────┐
│ CodeGenerator│ │ PRGenerator │  │  ReviewBot    │
│  (6 types)   │ │ (titles +   │  │ (inline +     │
│              │ │  body tmpl) │  │  summary)     │
└──────────────┘ └─────────────┘  └───────────────┘
        │               │                  │
        └───────────────┴──────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 GitHub REST API                      │
│   branch → commit → PR → review → approve → merge   │
└─────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---------|---------|
| **6 Change Types** | `feature`, `fix`, `refactor`, `docs`, `perf`, `test` — weighted randomly |
| **Realistic Branch Names** | `feature/user-auth-0428`, `fix/null-pointer-login-0428` |
| **Conventional Commits** | `feat(api): implement user-auth service` |
| **Professional PR Templates** | Full body with Summary, Motivation, Changes, Checklists |
| **Automated Review** | Inline comments + overall summary in reviewer persona |
| **Auto Approve & Merge** | Approval after organic delay, squash or merge |
| **Retry Logic** | Exponential backoff with jitter on all API calls |
| **Rate Limit Handling** | Automatic wait on GitHub API rate limit headers |
| **Organic Scheduling** | Random delay (0–60min) applied before execution |
| **Weekly Maintenance** | Auto-prune stale branches, activity reports |
| **Failure Alerts** | Auto-creates GitHub Issues on workflow failures |
| **Quality Gate** | Linting, formatting, type checks, test coverage |

---

## Project Structure

```
devflow-automator/
├── .github/
│   └── workflows/
│       ├── daily-automation.yml    # Main orchestrator workflow
│       ├── auto-merge.yml          # PR review + merge workflow
│       └── weekly-maintenance.yml  # Cleanup + reporting
│
├── scripts/
│   ├── orchestrator.py             # Main entry point — full lifecycle
│   ├── post_review.py              # Post a review on a specific PR
│   ├── merge_pr.py                 # Approve + merge a specific PR
│   ├── maintenance.py              # Branch pruning + cleanup
│   ├── weekly_report.py            # Activity report generator
│   └── cleanup.py                  # Failure cleanup
│
├── src/
│   ├── generators/
│   │   ├── code_generator.py       # Produces realistic code changes
│   │   └── pr_generator.py         # PR titles + body templates
│   ├── reviewers/
│   │   └── review_bot.py           # Automated review comments
│   └── utils/
│       ├── github_client.py        # GitHub REST API client
│       ├── logger.py               # Structured logging setup
│       └── retry.py                # Retry with exponential backoff
│
├── config/
│   └── settings.py                 # Environment-based configuration
│
├── tests/
│   └── test_core.py                # Unit + integration test suite
│
├── docs/
│   └── api.md                      # API reference
│
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Fork & Clone

```bash
git clone https://github.com/DeepDN/Github-automation.git
cd Github-automation
```

### 2. Create GitHub Personal Access Tokens (PATs)

You need **two GitHub accounts** — one to author PRs, one to approve them (GitHub blocks self-approval).

#### Main Account Token (`DEVFLOW_PAT`)

Go to: **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**

Required permissions:
- `Contents` — Read & Write
- `Pull requests` — Read & Write
- `Issues` — Read & Write
- `Metadata` — Read

#### Reviewer Account Token (`REVIEWER_PAT`)

Log into your **second GitHub account** and generate a Fine-grained token for the same repository.

Required permissions:
- `Pull requests` — Read & Write
- `Metadata` — Read

### 3. Add GitHub Actions Secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `DEVFLOW_PAT` | Main account PAT (creates branches, commits, PRs, merges) |
| `REVIEWER_PAT` | Second account PAT (approves PRs) |
| `GIT_USER_NAME` | Your main GitHub display name |
| `GIT_USER_EMAIL` | Your main GitHub email address |

> **Note:** `REVIEWER_PAT` is optional. If not set, the approval step is skipped and PRs are merged directly. All other activity (commits, PRs, reviews, merges) still counts on your contribution graph.

### 4. Enable GitHub Actions

Go to **Actions tab** → click **"I understand my workflows, go ahead and enable them"**

### 5. Test Manually

Go to **Actions → DevFlow Daily Automation → Run workflow** and select a change type.

### 6. (Optional) Local Development

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export GITHUB_TOKEN=your_pat
export REPO_OWNER=your_username
export REPO_NAME=your_repo

# Dry run (no real changes)
python scripts/orchestrator.py --dry-run --verbose

# Real run with specific change type
python scripts/orchestrator.py --change-type feature
```

---

## Configuration

All configuration is via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | ✅ | — | Main account PAT — creates branches, commits, PRs, merges |
| `REVIEWER_PAT` | ❌ | — | Second account PAT — approves PRs (skipped if not set) |
| `REPO_OWNER` | ✅ | — | Repository owner (GitHub username/org) |
| `REPO_NAME` | ✅ | — | Repository name |
| `PROJECT_NAME` | ❌ | `devflow-automator` | Used in commit messages |
| `REVIEWER_NAME` | ❌ | `auto-reviewer` | Name used in review comments |
| `DEFAULT_BRANCH` | ❌ | `main` | Target branch for PRs |
| `DRY_RUN` | ❌ | `false` | Simulate without making changes |

---

## Workflow Details

### Daily Automation (`daily-automation.yml`)

**Trigger:** Cron schedule, Mon–Sat at varied UTC times + manual dispatch

**Steps:**
1. **Pre-flight** — validate secrets, select change type (weighted random)
2. **Quality Gate** — lint, format check, mypy, pytest
3. **Orchestrator** — full PR lifecycle with organic delay
4. **Failure Alert** — creates GitHub Issue on failure

### Auto Review + Merge (`auto-merge.yml`)

**Trigger:** PR opened to `main` + manual dispatch

**Steps:**
1. **CI Checks** — lint, test, security scan (bandit)
2. **Auto Review** — wait 30–150s, post inline comments + summary
3. **Auto Merge** — wait 60–240s, approve via `REVIEWER_PAT` (second account), squash/merge via `DEVFLOW_PAT`, delete branch

### Weekly Maintenance (`weekly-maintenance.yml`)

**Trigger:** Every Sunday at 08:00 UTC

**Steps:**
1. Prune branches older than 7 days
2. Close stale automation issues
3. Generate weekly activity JSON report

---

## Change Type Distribution

The system uses weighted random selection to produce realistic commit patterns:

| Type | Weight | Frequency |
|------|--------|-----------|
| `feature` | 30 | ~30% of PRs |
| `fix` | 25 | ~25% of PRs |
| `refactor` | 20 | ~20% of PRs |
| `perf` | 10 | ~10% of PRs |
| `docs` | 10 | ~10% of PRs |
| `test` | 5 | ~5% of PRs |

---

## Tech Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| Language | Python 3.11 | Readable, strong typing, rich stdlib |
| API Client | `requests` | Reliable, simple HTTP |
| CI/CD | GitHub Actions | Native integration, free for public repos |
| Config | Environment Variables | 12-factor app compliance |
| Testing | pytest + unittest.mock | Fast, expressive |
| Code Quality | flake8 + black + mypy | Industry standard toolchain |
| Security | bandit | Static security analysis |

---

## Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Important Notes

- All PRs and commits are made under **your GitHub identity** (via your PAT) — contributions will count on your profile graph
- PR approvals are made by the **second GitHub account** (`REVIEWER_PAT`) — GitHub blocks self-approval, so two tokens are required for a full review → approve → merge lifecycle
- If `REVIEWER_PAT` is not configured, the approval step is skipped gracefully and PRs are merged directly
- The organic delay system (random 0–60 min sleep) prevents identical timestamp patterns
- Branch naming, commit messages, and PR content use professional vocabulary pools to avoid repetition
- The system handles GitHub API rate limits automatically

---

## License

MIT — see [LICENSE](LICENSE)

---

*DevFlow Automator — built to showcase production-grade GitHub automation engineering.*
