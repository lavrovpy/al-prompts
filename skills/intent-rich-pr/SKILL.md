---
name: intent-rich-pr
description: Create GitHub pull requests with intent-rich descriptions that explain why the change exists, link ticket or issue context, summarize the diff, capture reviewer-facing decision rationale, and include validation. Use when the user asks to create, open, draft, or write a PR/MR and wants reviewers or AI review agents to understand the underlying motivation, reasoning, tradeoffs, or issue context.
---

# Intent-Rich PR

## Overview

Use this skill to create a pull request whose description gives reviewers the missing context behind the diff. The output should help human and AI reviewers understand the motivation, important decisions, course corrections, and validation before inspecting changed files.

## Workflow

1. Confirm the repository state.
   - Run `git status -sb`.
   - Identify the current branch, upstream, base branch, commits, and changed files.
   - If the worktree has unrelated uncommitted changes, stop and ask what belongs in the PR.

2. Collect motivation before drafting.
   - Ask for or derive the original user request, ticket, GitHub issue, Jira issue, Linear issue, design doc, or incident context.
   - If a ticket or issue exists, include its link in the PR body.
   - If a GitHub issue is referenced and accessible, fetch its title/body with `gh issue view` or the available GitHub connector.
   - If an external ticket is referenced but unavailable, ask the user to paste the relevant description or summarize it.
   - Do not invent ticket context. If there is no ticket, say so in the PR body and use the user request as the motivation.

3. Inspect the implementation.
   - Review `git log <base>..HEAD`, `git diff --stat <base>...HEAD`, and the relevant diff.
   - Identify what changed, why the chosen implementation fits the motivation, and what reviewer risks remain.
   - Prefer concrete file/module names over vague summaries.

4. Capture decision rationale.
   - Include reviewer-facing reasoning only: important decisions, rejected alternatives, tradeoffs, assumptions, and course corrections that explain why the diff looks this way.
   - Do not include raw hidden chain-of-thought or speculative inner monologue.
   - If the implementation changed direction during the work, summarize the reason and final choice.
   - If nothing unusual happened, keep this section short.

5. Draft the PR body.
   - Read `references/pr-body-guide.md` before drafting.
   - Use real Markdown prose with clear headings.
   - Put reviewer context and motivation before the diff summary.
   - Explicitly tell AI/code-review agents to read the description before reviewing when that is relevant.
   - Include validation commands and results, or state what was not run.

6. Create the PR.
   - Default to a draft PR unless the user explicitly asks for a ready PR.
   - Prefer `gh pr create --body-file <temp-file>` or the available GitHub connector so Markdown renders correctly.
   - Use a concise title that reflects the whole branch.
   - After creation, return the PR URL, base branch, head branch, draft status, and any missing validation.

## PR Body Requirements

Every intent-rich PR body should include:

- **Reviewer context:** A short instruction telling reviewers what context matters before reading the diff.
- **Motivation:** The user request, ticket/issue summary, and ticket/issue link when available.
- **Decision rationale:** Key implementation reasoning that is useful for review.
- **What changed:** A concise diff-oriented summary.
- **Validation:** Commands/checks run and their results.

Optional sections:

- **Risk or follow-up:** Known gaps, intentionally deferred work, migration concerns, or manual checks.
- **Screenshots or artifacts:** Only when relevant to UI or generated asset work.

## Quality Rules

- Keep the PR description useful, not ceremonial.
- Do not pad the body with generic boilerplate.
- Do not claim that a ticket, issue, test, or review happened unless verified.
- Preserve the user's stated intent even when the diff summary is shorter.
- Make the causal chain clear: ticket/user need -> implementation choice -> changed files -> validation.
