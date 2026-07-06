---
name: pr-batch-triage
description: Performs a rapid, first-pass evaluation of a batch of incoming pull requests to categorize them by risk and complexity. Use when you have a backlog of PRs and need to decide where to focus human review first.
---

# PR Batch Triage

## Overview
Perform a high-level, fast assessment of a batch of pull requests. The goal is to separate low-risk changes that are likely safe from complex or high-risk changes that require deep human inspection. Do not auto-merge or perform deep-dive line-by-line review here; focus on attention allocation.

## When to Use
- When starting a review session with multiple pending pull requests.
- When organizing a team's code review queue.

## Triage Classification Criteria

Evaluate each PR and classify it into one of three buckets:

### 1. Low-Risk (Likely Safe to Merge)
- **Scope:** Small diff size (e.g., < 50 lines changed).
- **Type:** Documentation, comments, simple typo fixes, or non-breaking minor dependency version bumps.
- **Tests:** Pure test-addition PRs that don't modify production code, or simple changes where existing test suites run and pass.

### 2. Needs Work / Review (Medium Risk)
- **Scope:** Moderate diff size (e.g., 50–300 lines changed).
- **Type:** Standard feature additions, UI/UX changes, or straightforward refactoring.
- **Indicators:** Missing test coverage for new branches, slight code-style mismatches, or minor architectural coupling.

### 3. High-Risk (Requires Deep Human Audit)
- **Scope:** Large diff size (> 300 lines changed) or high-complexity.
- **Type:** Database schema migrations, authentication/authorization updates, cryptographic logic, performance-critical hot paths, or changes to shared infrastructure.
- **Indicators:** Deletes critical tests, introduces new external dependencies, or contains structural changes that bypass security boundaries.

## Core Process

1. **Scan the Batch:** Retrieve metadata (author, branch, file names, diff size) for the target batch of PRs.
2. **Run Quick Checks:** Verify if unit tests and builds passed in CI for each PR.
3. **Classify:** Apply the triage criteria above to categorize each PR.
4. **Produce Triage Report:** Output a structured summary designed for quick reading.

## Triage Report Template

```markdown
# PR Batch Triage Report

## Summary Queue
- 🟢 **Low-Risk (Safe to Merge):** PR #123, PR #128
- 🟡 **Needs Work / Standard Review:** PR #124, PR #125
- 🔴 **High-Risk (Requires Audit):** PR #126, PR #127

---

### 🔴 High-Risk Details
#### PR #126: "Add user-role check to DB query"
- **Risk Reasons:** Modifies core authorization gates; potential for SQL injection or privilege escalation.
- **Key Files:** `src/db/auth.ts`
- **Attention Allocation:** Requires a security specialist or senior developer audit.

### 🟡 Needs Work / Standard Review Details
#### PR #124: "Implement tasks filter dropdown"
- **Risk Reasons:** Standard feature but is missing unit tests for the new filtering reducer logic.
- **Attention Allocation:** Suggest asking the author for tests before starting human code review.
```

## Common Rationalizations
| Rationalization | Reality |
|---|---|
| "I should just review the first one line-by-line right now." | Triaging first allows you to quickly merge low-risk items and unblock colleagues before investing long chunks of time in complex ones. |
| "A small diff is always low-risk." | A 1-line change to auth config or database rules can be highly risky. Assess file paths and context, not just diff size. |

## Red Flags
- Classifying a PR as low-risk just because the diff is small (e.g. changing configurations, credentials, dependency versions, or database keys).
- Performing deep, multi-line comment code reviews during the triage stage.
- Recommending auto-merging of approved PRs without any human oversight.

## Verification
- [ ] Every PR in the batch is assigned to exactly one risk category (Low, Medium, High).
- [ ] Reasons for High-Risk and Medium-Risk classifications are explicitly documented.
- [ ] CI/CD run status is verified for each PR.
