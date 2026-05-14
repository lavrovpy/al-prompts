---
name: self-reflection
description: Analyze past Claude Code session logs to surface agent failure modes — failed tool calls, inability to find relevant code, context confusion or distraction, and stale edits — and produce a Markdown report grouped by repository with likely cause and possible fix for each issue. Use this skill whenever the user asks Claude to "reflect on past sessions", "audit my logs", "where did the agent struggle", "find failure modes", "self-reflect", "/self-reflection", "what went wrong in recent sessions", or any retrospective request about Claude Code's own behavior across `~/.claude/projects/`. Trigger even if the user does not explicitly mention logs — phrases like "be honest about where you got stuck" or "look back at what I asked you to do this week and find the rough patches" should also invoke this skill.
argument-hint: "[repo|all] [count|all]"
arguments: [repo, count]
---

# Self-Reflection

Reads Claude Code session transcripts under `~/.claude/projects/` and produces an honest, structured report of the failure modes the agent exhibited — so the user can adjust their prompting, fix flaky tools, or update CLAUDE.md to dodge repeat mistakes.

The point is not to summarize what got done (that's [[session-summary]]). The point is to find where the agent *struggled* — the rough edges that a casual diff review wouldn't reveal.

## Arguments

Both arguments are optional and positional.

- **`$repo`** — Which repository to analyze. Accepts:
  - Empty or `all` → analyze every repository under `~/.claude/projects/` (default).
  - An absolute path like `/Users/alavreniuk/Dev/al-prompts` → only that repo.
  - A short name like `al-prompts` → match against the decoded cwd of each project dir; if exactly one repo matches, use it. If multiple match, list them and ask which one.
  - A path-encoded dir name like `-Users-alavreniuk-Dev-al-prompts` → use that project dir directly.
- **`$count`** — Maximum number of sessions to analyze **per repository**. Accepts:
  - Empty or `all` → analyze every session per repo (default).
  - A positive integer like `5` → take the `$count` most-recently-modified `.jsonl` files in each in-scope repo (still excluding the currently-running session — see "Notes on scope" below).

If only one argument is given, it's `$repo`. To pass only `$count`, pass `all` as the first argument: `/self-reflection all 10`.

**Examples**:
- `/self-reflection` → every repo, every session.
- `/self-reflection al-prompts` → just the `al-prompts` repo, every session.
- `/self-reflection al-prompts 5` → just `al-prompts`, last 5 sessions.
- `/self-reflection all 3` → every repo, last 3 sessions each.

If the arguments are missing entirely (the user invoked the skill via natural language with no explicit numbers or repo names), treat both as their defaults — do not interrupt to ask. The report itself will state the scope it used so the user can re-run with narrower arguments if they want.

## What counts as a failure

These four categories cover the bulk of useful failure signal. Bias toward inclusion: if a stretch of the transcript looks like wasted effort, log it.

1. **Failed tool calls** — non-zero exits, validation errors, permission denials, repeated retries of the same command, edits that error because the file wasn't read first, tool calls that return empty/wrong results and the agent doesn't notice.
2. **Inability to find relevant code** — extended grep/glob loops that don't converge, the agent asks the user where something is after >3 search attempts, the agent gives up and writes new code that duplicates existing code, the agent reads many irrelevant files before finding the right one.
3. **Context confusion / distraction** — the agent answers a different question than was asked, goes off on a tangent, repeats work already done earlier in the session, "forgets" a constraint the user stated explicitly, confuses two similarly-named files/functions.
4. **Stale edits** — the agent edits based on a stale read (the file changed since), reapplies a change that was already reverted, undoes a prior edit by accident, the `old_string` doesn't match because the file was edited elsewhere.

If you spot something interesting that doesn't fit these four — flaky MCP servers, looping subagent spawns, unbounded thinking, hallucinated file paths — include it under a "Other" category in that repository's table.

## How to execute

### Step 1: Inventory the logs

List `~/.claude/projects/`. Each subdirectory is one repository (a path-encoded cwd: slashes replaced with dashes — e.g. `-Users-alavreniuk-Dev-al-prompts` ⇒ `/Users/alavreniuk/Dev/al-prompts`). Within each subdirectory, `*.jsonl` files are individual session transcripts.

**Apply the `$repo` filter first:**
- If `$repo` is empty or `all` → keep all project directories.
- If it's an absolute path → keep only the project dir whose decoded cwd matches.
- If it's a path-encoded name (starts with `-`) → keep that exact dir.
- Otherwise, treat it as a short name: keep project dirs whose decoded cwd's last path segment equals `$repo`. If zero match, tell the user and stop. If more than one matches, list the candidates and ask which one.

**Then apply the `$count` filter per repo:**
For each surviving project dir, list its `.jsonl` files sorted by mtime (newest first), exclude the most-recently-modified file (the currently-running session), and:
- If `$count` is empty or `all` → keep all remaining files.
- Otherwise → keep the top `$count` files.

Build a flat list of every kept `.jsonl` path alongside the repository it belongs to. **Do not open the files yet** — the subagents will do that.

If the list is empty (no projects, no sessions after filtering), tell the user and stop — there's nothing to reflect on.

### Step 2: Partition across 10 subagents

Split the .jsonl files into **10 roughly-equal groups** by count. If there are fewer than 10 files, spawn one subagent per file instead — spawning empty subagents wastes tokens.

Keep files from the same repository together where possible (don't split a 4-session repo across 4 different subagents) — this gives each subagent enough context to spot patterns within a repo, like "the agent kept failing on the same import." When a repository has more sessions than fit in one bucket, splitting it is fine; the aggregation step will rejoin the findings.

### Step 3: Spawn the subagents in parallel

Send all subagent tasks **in a single message** with multiple Agent tool calls so they run concurrently. Use `subagent_type: "general-purpose"` (or `Explore` if available and read-only — these subagents only read).

Each subagent's prompt should include:

- The exact list of `.jsonl` paths assigned to it (absolute paths).
- The four failure categories from above (paste them verbatim — don't make the subagent guess).
- The repository name(s) those files belong to, so it can attribute findings.
- A request to return a **JSON-shaped response** (described below) so aggregation is mechanical, not a re-summarization exercise.

Subagent return format — ask for exactly this structure:

```json
{
  "findings": [
    {
      "repository": "/Users/alavreniuk/Dev/al-prompts",
      "session_file": "abc123.jsonl",
      "category": "failed_tool_calls" | "inability_to_find_code" | "context_confusion" | "stale_edits" | "other",
      "description": "one-sentence concrete description of what happened",
      "evidence": "a short quote or summary from the transcript that proves it",
      "likely_cause": "best guess at why it happened",
      "possible_fix": "actionable suggestion (prompt change, CLAUDE.md rule, tool fix, etc.)"
    }
  ]
}
```

Tell the subagent: **be specific, not generic**. "Failed tool calls" is useless. "`Edit` failed 3 times in `auth.py` because the file was modified by a subagent between reads" is useful. Quote line numbers or short snippets where possible — they're the evidence that anchors each finding.

Tell the subagent to **skip non-failures**. A successful 4-hour session that produced a working feature should generate zero findings. We're not looking for things the agent did; we're looking for things it bumbled.

### Step 4: Aggregate

Collect the `findings` arrays from all subagents into one list. Then:

1. **Group by repository** — bucket findings by their `repository` field. Decode any path-encoded names back to real paths (`-Users-alavreniuk-Dev-foo` ⇒ `/Users/alavreniuk/Dev/foo`).
2. **De-duplicate within a repository** — if multiple subagents reported essentially the same issue (same category, same description gist), merge them and note the count.
3. **Sort within each repository** — by category, then by frequency (most-frequent first).

If a single repository's findings would produce a >25-row table, keep only the top 25 by frequency and add a note: "20 additional lower-priority findings omitted."

### Step 5: Write the report

Write the report to `self-reflection-<YYYY-MM-DD>.md` in the current working directory (so it lands wherever the user invoked the skill from, not buried in `~/.claude/`).

Use this exact structure:

```markdown
# Self-Reflection Report — <YYYY-MM-DD>

**Scope**: repo=`<$repo or "all">`, count=`<$count or "all">` — analyzed **<N>** session files across **<M>** repositories.

## /Users/alavreniuk/Dev/repo-one

| Category | Description | Likely Cause | Possible Fix |
| --- | --- | --- | --- |
| Failed tool call | `Edit` errored 5× on `src/auth.py` — `old_string` not unique | The file has repeated boilerplate; the agent picked too-narrow context | Read the file first and quote a unique surrounding block, or use `replace_all` |
| Stale edit | Agent re-added a `console.log` that was removed two messages earlier | Long context — earlier removal scrolled out of working memory | Add a "no debug logging in commits" rule to CLAUDE.md |
| Context confusion | Agent ran tests for `api/` after user explicitly asked about `web/` | Similar directory names; user's prompt was terse | When the user mentions a directory, restate it before acting |

## /Users/alavreniuk/Dev/repo-two

| Category | Description | Likely Cause | Possible Fix |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

## Cross-repository patterns

- _(Optional)_ If the same failure recurs across multiple repos (e.g., "Edit's `old_string` uniqueness is a frequent footgun across all 4 projects"), call it out here in a short bulleted list. Skip this section entirely if there are no cross-cutting patterns.
```

Rules for the tables:
- One row per finding (after dedup). The frequency note goes inline in the **Description** column (e.g., "Edit errored on `auth.py` (3 sessions)").
- Use Markdown pipes — don't try to align with spaces; renderers handle it.
- Keep cells short. Long evidence quotes go after the table as footnotes, not inline.
- Category column values: `Failed tool call`, `Inability to find code`, `Context confusion`, `Stale edit`, `Other`. Use the human-readable form, not the JSON enum.

### Step 6: Tell the user where the report is

After writing the file, briefly tell the user the path and a one-sentence headline of the most interesting pattern you found (e.g., "Wrote `self-reflection-2026-05-14.md` — the most common failure was repeated `Edit` errors from non-unique `old_string` across 4 repos.").

## Notes on scope

- **Default scope is all projects** under `~/.claude/projects/`. The whole point of the per-repository grouping is to compare patterns across them. If the user explicitly says "just this repo" or "just the current project", narrow it to the one matching project directory (encode cwd by replacing `/` with `-`).
- **Skip the currently-running session.** Its transcript is still being written and the agent can't honestly reflect on a session it's mid-way through. Sort each project's `.jsonl` files by mtime and exclude the most-recently-modified one.
- **Don't grade yourself favorably.** The skill is most valuable when it surfaces uncomfortable findings. If a category has zero findings across all logs, say so explicitly — that's also a signal, not something to hide.
