---
name: self-reflection
description: Read past Claude Code session logs to find what the agent learned the hard way — failed approaches, missed constraints, facts it had to dig for — and turn the durable, non-obvious ones into CLAUDE.md / AGENTS.md lines so future agents start out knowing them. Use whenever the user asks Claude to "reflect on past sessions", "audit my logs", "what should be in CLAUDE.md", "where did the agent struggle", "self-reflect", "/self-reflection", or any retrospective about Claude Code's own behavior across `~/.claude/projects/`. Trigger even without the word "logs" — e.g. "look back at this week and tell me what tripped you up".
argument-hint: "[repo|all] [count|all]"
arguments: [repo, count]
---

# Self-Reflection

Read past session transcripts under `~/.claude/projects/`, find the moments where the agent **struggled and then discovered something it should have known from the start**, and output that knowledge as lines ready to drop into the repo's `CLAUDE.md` / `AGENTS.md`.

Classic example: the agent ran `npm install`, it failed, the agent checked `package.json`, found `pnpm` — and only then moved on. The durable lesson is "this project uses pnpm". A future agent should know that on line one instead of rediscovering it.

This is not a session summary ([[session-summary]] does that). The output is the *memory file*, not a write-up of what happened.

## Arguments

Both optional and positional.

- **`$repo`** — `all` or empty → every repo (default). An absolute path, a short name (matched against each project's decoded cwd), or a path-encoded dir name (`-Users-me-Dev-foo`) → just that repo. If a short name matches more than one repo, list them and ask.
- **`$count`** — `all` or empty → every session (default). An integer → the N most recent sessions per repo.

To pass only a count: `/self-reflection all 10`. Invoked via natural language with no numbers → use defaults; don't interrupt to ask.

## What to harvest

Scan each transcript for friction, then ask of every rough patch: **"What fact, known upfront, would have avoided this?"** Keep only facts that are:

- **Durable** — true next session too (a tool choice, a path, a convention, a gotcha), not a one-off bug.
- **Non-obvious** — the agent wasted real effort finding it, or got it wrong first.
- **Worth the context budget** — see the filter below.

Good signals: wrong command/tool tried first (`npm` vs `pnpm`, wrong test runner, wrong build step); a constraint the user had to repeat; a file or service the agent hunted for across many searches; an environment assumption that bit it (dev server already running, required env var, monorepo layout); a convention it violated and was corrected on.

## The filter — less is more

`CLAUDE.md` loads into context every single turn, so every line must earn its place. Before keeping a fact, apply:

- **If it's easy to find, let the agent find it.** Anything one glance at an obvious place reveals — a `scripts` entry in `package.json`, a README heading, an obvious lockfile — does **not** go in. Add a fact only when the *obvious* path misleads or the discovery cost was real.
- **No duplicates.** Read the repo's existing `CLAUDE.md` / `AGENTS.md` first and skip anything already covered.
- **No generic advice.** "Write tests", "handle errors" — never. Only project-specific facts.
- **No secrets.** No keys, tokens, or credentials.
- **Prefer recurring pain.** A struggle seen across several sessions beats a single stumble.

When in doubt, leave it out. A short, sharp `CLAUDE.md` is the goal.

## How to execute

1. **Inventory.** List `~/.claude/projects/`. Each subdir is one repo (path-encoded cwd: dashes are slashes). Apply `$repo`, then per surviving repo list `*.jsonl` by mtime, **drop the newest (the currently-running session)**, and keep `$count` of the rest. Empty result → tell the user, stop.
2. **Scan.** Transcripts are large. If a repo has many sessions, fan out: split its `.jsonl` files across parallel read-only subagents (`Explore` or `general-purpose`), one group each, and have each return the harvested facts (fact + the evidence snippet that justifies it + which CLAUDE.md section it belongs to). Few files → just read them directly.
3. **Distill.** Pool the facts, dedup, drop everything the filter rejects, and read each repo's existing memory file to avoid repeats.
4. **Output** (below). Then offer to append the lines to each repo's `CLAUDE.md` / `AGENTS.md` — only edit after the user confirms.

## Output format

Group by repository (memory files are per-repo). Under each, write paste-ready Markdown organized into the standard `CLAUDE.md` sections — use only the sections you actually have facts for:

- **Common Commands** — the right command when the obvious one is wrong.
- **Standards** — conventions the agent violated and was corrected on.
- **Key Directories** — layout the agent had to hunt for.
- **Notes** — gotchas, environment assumptions, anything else durable.

```markdown
## /Users/me/Dev/foo

### Common Commands
- Use `pnpm`, not `npm` — this is a pnpm workspace. (3 sessions started with a failed `npm install`)

### Notes
- The dev server is assumed already running; don't start it.
- Integration tests need `DATABASE_URL` set, or they hang silently.
```

Keep each line one sentence. Put the *why* (the evidence) in a short parenthetical only when it helps the user trust the line — not a paragraph. If a repo yields nothing worth adding, say so plainly; an empty result is a valid, honest outcome.
