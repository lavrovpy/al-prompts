---
name: review-branch
description: Review the current branch against its base with Claude Code's and Codex's reviewers while every runnable test suite runs, then fix verified findings in priority order, P0 first.
disable-model-invocation: true
argument-hint: "[base]"
arguments: base
allowed-tools: Read, Grep, Glob, Edit, Bash(mktemp:*), Bash(claude -p:*), Bash(codex review:*), Bash(git fetch:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git status:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Bash(git worktree:*), Bash(uv run:*), Bash(npm test:*), Bash(npm run:*)
---

# Review branch

`<base>` below is `$base`; when that is empty, the remote's default branch from `git symbolic-ref --short refs/remotes/origin/HEAD`.

1. **Pin the diff.** `git fetch origin`, then `git diff --stat <base>...HEAD`. Stop if the ref fails to resolve or the diff is empty.

2. **Start reviewers and tests.** `OUT=$(mktemp -d)`. From the repo root, start each of these as its own `run_in_background` Bash call, all in one response:

   ```bash
   claude -p "Use the code-review skill to review the changes since <base>. Report findings only. Where a spec or issue tracker is missing, skip that axis and say so." \
     --model claude-opus-5-5 --effort high \
     --allowedTools "Skill Agent Read Grep Glob Bash(git diff:*) Bash(git log:*) Bash(git show:*) Bash(git rev-parse:*)" > "$OUT/claude.md" 2>&1

   codex review -c model=gpt-6.1-sol -c model_reasoning_effort=high -c sandbox_mode=read-only --base <base> > "$OUT/codex.md" 2>&1
   ```

   The models and effort are defaults; swap them when the user names others.

   Plus every test suite the repo documents (`AGENTS.md`, READMEs, `Makefile`, `package.json`), each whole, to `$OUT/tests-<suite>.log`. Skip a suite only when this machine lacks what it needs (a credential, a cluster, a live service), and record what was missing.

3. **Wait.** End the turn; completion notifications wake you. Read every output file in full. A reviewer that failed or wrote nothing goes in the report; continue with the other.

4. **Triage.** Merge both reports and every failing test into one list, one entry per problem. Open the cited code and give each entry a priority:

   - **P0** critical: data loss, security breach, broken production behaviour
   - **P1** high: a bug under normal use
   - **P2** medium: a bug under edge conditions, or a design, types, config or error-handling issue worth fixing in this branch
   - **P3** low: a minor issue, or an idea fine to defer to a ticket

   Drop an entry you cannot see in the code, and say why. A failing test the diff does not explain: rerun it at the merge-base in a throwaway worktree; if it fails there too, report it and leave it.

5. **Fix.** P0 first, then P1, then P2, each only where the fix is local and unambiguous. Report P3 unfixed. Then rerun every suite from step 2: a test that passed before and fails now means revert the fix that broke it.

6. **Report.** Findings by priority, each fixed or not with a one-line reason; per-suite pass and fail counts before and after; suites and reviewers that did not run. Last line: git state from `git status -sb`. Leave committing and pushing to the user.
