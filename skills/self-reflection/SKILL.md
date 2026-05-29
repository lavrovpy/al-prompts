---
name: self-reflection
description: Read your AI coding agent's past session logs (Claude Code, Codex, Cursor, Gemini CLI, Aider, …) to find what it learned the hard way — failed approaches, missed constraints, facts it had to dig for — and turn the durable, non-obvious ones into the project's agent memory file (AGENTS.md, CLAUDE.md, or equivalent) so future sessions start out knowing them. Use whenever the user asks to "reflect on past sessions", "audit my logs", "what should be in AGENTS.md/CLAUDE.md", "where did the agent struggle", "self-reflect", "/self-reflection", or any retrospective about the agent's own behavior. Trigger even without the word "logs" — e.g. "look back at this week and tell me what tripped you up".
argument-hint: "[repo|all] [count|all]"
arguments: [repo, count]
---

# Self-Reflection

Read past session transcripts from whatever AI coding agent produced them, find the moments where the agent **struggled and then discovered something it should have known from the start**, and record that knowledge in the project's agent memory file so the next session starts already knowing it.

Classic example: the agent ran `npm install`, it failed, the agent checked `package.json`, found `pnpm` — and only then moved on. The durable lesson is "this project uses pnpm". A future session should know that on line one instead of rediscovering it.

This is not a session summary. The output is the *memory file*, not a write-up of what happened.

## The memory file

Write the result into the project's agent-instruction file — whichever the project (or the running agent) already uses:

- **AGENTS.md** — cross-agent standard (Codex, Cursor, and others); the safe default if none exists yet.
- **CLAUDE.md** — Claude Code.
- **GEMINI.md** and similar — match the tool.

If several exist, update the one the project actually keeps current. If none exists, create `AGENTS.md`.

## Arguments

Both optional and positional.

- **`$repo`** — `all` or empty → every repo found in the logs (default). An absolute path or a short name → just that repo. If a short name matches more than one repo, list them and ask.
- **`$count`** — `all` or empty → every session (default). An integer → the N most recent sessions per repo.

To pass only a count: `/self-reflection all 10`. Invoked via natural language with no numbers → use defaults; don't interrupt to ask.

## What to harvest

Scan each transcript for friction, then ask of every rough patch: **"What fact, known upfront, would have avoided this?"** Keep only facts that are:

- **Durable** — true next session too (a tool choice, a path, a convention, a gotcha), not a one-off bug.
- **Non-obvious** — the agent wasted real effort finding it, or got it wrong first.
- **Worth the context budget** — see the filter below.

Good signals: wrong command/tool tried first (`npm` vs `pnpm`, wrong test runner, wrong build step); a constraint the user had to repeat; a file or service the agent hunted for across many searches; an environment assumption that bit it (dev server already running, required env var, monorepo layout); a convention it violated and was corrected on.

## The filter — less is more

The memory file loads into the agent's context on every turn, so every line must earn its place. Before keeping a fact, apply:

- **If it's easy to find, let the agent find it.** Anything one glance at an obvious place reveals — a `scripts` entry in `package.json`, a README heading, an obvious lockfile — does **not** go in. Add a fact only when the *obvious* path misleads or the discovery cost was real.
- **No duplicates.** Read the existing memory file first and skip anything already covered.
- **No generic advice.** "Write tests", "handle errors", and tool-contract trivia (read-before-edit, token limits) are true in every repo and for every agent — never include them. Only project-specific facts.
- **No secrets.** No keys, tokens, or credentials.
- **Prefer recurring pain.** A struggle seen across several sessions beats a single stumble; a fact the *user* stopped to correct is the strongest signal of all.

When in doubt, leave it out. A short, sharp memory file is the goal.

## How to execute

1. **Locate the logs.** Find where the running agent stores its session transcripts, then filter to the target repo (`$repo`) and the `$count` most-recent sessions, skipping the currently-running session (usually the newest by mtime). Common locations:
   - **Claude Code** — `~/.claude/projects/<dir>/*.jsonl`; one dir per repo, named by the repo's path with `/` replaced by `-`.
   - **Codex CLI** — `~/.codex/sessions/` (`*.jsonl` rollout files).
   - **Cursor** — workspace-storage SQLite under `~/Library/Application Support/Cursor/User/workspaceStorage/`.
   - **Aider** — `.aider.chat.history.md` in the repo.
   - If you don't recognize the agent, ask the user where its history lives. Empty result → say so, stop.
2. **Scan.** Transcripts can be large. If the agent can spawn parallel read-only sub-tasks, split the files across them; otherwise read directly, grepping big files for friction (errors, retries, user corrections) rather than reading linearly. Each scan returns the harvested facts + the evidence snippet that justifies each + its target section.
3. **Distill.** Pool the facts, dedup, drop everything the filter rejects, and read the existing memory file to avoid repeats.
4. **Output** (below). Then offer to append the lines to the memory file — only edit after the user confirms.

## Output format

Group by repository (memory files are per-repo). Under each, write paste-ready Markdown organized into standard sections — use only the sections you actually have facts for:

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
