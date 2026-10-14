---
name: intent-rich-pr
description: Create GitHub pull requests with intent-rich descriptions that explain why the change exists, link ticket or issue context, summarize the diff, capture reviewer-facing decision rationale, identify review risk, and include validation. Use when the user asks to create, open, draft, or write a PR/MR and wants reviewers or AI review agents to understand the underlying motivation, reasoning, tradeoffs, risk, or issue context.
---

# Intent-Rich PR

Create a pull request whose description gives reviewers what the diff cannot: why the change exists, what was decided along the way, where to look, and what was verified. The PR body is review intake for humans and AI reviewers alike.

## Gather

- **Repository state.** `git status -sb`, the current branch and its base, `git log <base>..HEAD`, `git diff --stat <base>...HEAD`, and the diff itself. If the worktree holds unrelated uncommitted changes, ask what belongs in the PR before going on.
- **Motivation.** The original request, ticket, issue, design doc, or incident. Fetch a referenced GitHub issue with `gh issue view` or the GitHub connector; for a tracker you cannot reach, ask the user to paste the relevant part. Never invent ticket context: when there is none, say so and use the user's request as the motivation.
- **Decision rationale** a reviewer would want: important decisions, rejected alternatives, tradeoffs, assumptions, and course corrections that explain why the diff looks the way it does. For agent-authored work, preserve the plan and intent so the reviewer does not have to reconstruct them. Keep it short when nothing unusual happened, and never paste raw chain-of-thought.
- **Review risk**, matched to blast radius rather than authorship: user-facing behaviour, data handling, auth, payments, security, migrations, CI, core business logic. Read test and CI changes closely and say when tests were rewritten, skipped, weakened, or updated to match new behaviour. Large diffs, many touched files, generated output, and unclear ownership are also worth naming.

## Write

Read `references/pr-body-guide.md` and follow its template. Reviewer context and motivation come before the diff summary. Name concrete files and modules. Include the validation commands and their results, or state what was not run. Treat AI review output as a signal, not a merge verdict: a human owns the merge decision for any meaningful blast radius.

## Create

Default to a draft PR unless the user asks for a ready one. Use `gh pr create --body-file <file>` or the GitHub connector so the Markdown renders. Give it a concise title that covers the whole branch. Report the PR URL, base and head branches, draft status, and any validation still missing.

## Rules

- Never claim that a ticket, issue, test, or review exists unless you verified it.
- Keep the body useful, not ceremonial: no generic boilerplate.
- Make the causal chain visible: need, implementation choice, changed files, validation.
