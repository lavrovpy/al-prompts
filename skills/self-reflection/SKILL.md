---
name: self-reflection
description: Retro over a repo's recent coding-agent sessions. Finds detours and stale docs, proposes environment fixes that make the repo easier to navigate.
disable-model-invocation: true
argument-hint: "[repo] [count]"
arguments: repo count
---

# Self-reflection

A **retro** over the last few coding-agent sessions in one repository. The goal is a more navigable **environment**: every finding becomes a candidate change to the repo's pointers, docs, checks, or tooling, so the next session spends fewer tokens reaching the same place. The code the sessions produced is out of scope; that is a code review's job.

Load the `writing-for-agents` skill, when available, before drafting any candidate that edits a steering file, doc, or skill.

## Arguments

- `$repo`: the repository. Default: the git root of the current working directory. Accepts an absolute path, or a short name matched against the last path segment of your project directories; ask when more than one matches.
- `$count`: sessions to read. Default `10`.

## Steps

### 1. Collect the sessions

A repository's sessions include its worktrees: run `git -C <repo> worktree list --porcelain` and treat every listed path as the repo.

- **Claude Code**: `~/.claude/projects/<encoded>/*.jsonl`. `<encoded>` is the session's cwd with every non-alphanumeric character replaced by `-` (`/Users/me/.codex/x_y` → `-Users-me--codex-x-y`). The encoding is lossy, so confirm a candidate file by the `cwd` field in its records.
- **Codex**: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. The first line is a `session_meta` record; its `payload.cwd` is the session's cwd.
- **Other agents**: read only stores whose format is documented and locally readable; for anything else, ask the user where the transcripts live.

Keep files whose cwd is a repo path or below one. Sort the union by mtime, drop the session you are running in, and keep the newest `$count`. Done when you can list each kept file with its agent, cwd, and date. If none remain, say so and stop.

### 2. Read each session in a subagent

Dispatch one read-only subagent per session, all in a single message so they run in parallel. Give each only its file path, the agent that wrote it, the repo paths, the lenses below, and the return format. Every finding quotes the session's own record; a finding without a quote is dropped.

Transcripts are sensitive: evidence quotes stay short, and secret-like values, tokens, private URLs, customer data, and personal messages are redacted.

**Lenses**

- **Detour**: the stretch of tool calls between the agent needing something (a file, a command, a convention) and first reaching it. Record the target, where it actually lived, the calls spent getting there (searches, reads, failed commands), and what the agent read on the way. Asking the user for something the repo holds, or rewriting code that already existed, is a detour that never arrived. A fact the user stopped to correct is the strongest signal.
- **Stale doc**: the agent acted on a document (README, `AGENTS.md` / `CLAUDE.md`, `docs/`, a skill, a code comment) and the environment then contradicted it: a documented command failed, a path was missing, an API or flag had changed. Record the doc, the claim, and the contradicting evidence.

When the session shows them, also record: a mistake an **automated check** could have caught, a mistake the **reviewer** missed, a tool call that returned far more than it was worth (**tool economy**), and information the agent needed but could not reach (**information access**).

Return format:

```json
{"findings": [{
  "session": "<file>",
  "agent": "claude-code | codex | <other>",
  "lens": "detour | stale-doc | automated-check | reviewer | tool-economy | information-access",
  "target": "the file, fact, or command the agent was after",
  "what": "one specific sentence",
  "evidence": "short redacted quote or tool-call excerpt from the record",
  "cost": "tool calls spent, plus tokens when the record carries usage"
}]}
```

A smooth session returns an empty list.

### 3. Merge and filter

Pool the findings and merge the ones that share a **target**, keeping the session count: a detour to the same place in three sessions is one finding at three times the cost. Then keep only findings an environment change would prevent:

- **Easy finds stay out.** When one glance at the obvious place (a `package.json` script, a lockfile, a README heading) answers the question, the agent can keep finding it; a pointer earns its place only when the obvious path misleads or the discovery cost was real.
- **Project-specific only.** Advice true in every repo for every agent ("write tests", read-before-edit) is dropped.
- **Recurring pain first.** A struggle across several sessions outranks a single stumble.

Done when every remaining finding has a distinct target and survives the filter.

### 4. Route each finding to its fix

| Lens | Candidate fix |
| --- | --- |
| Detour | A **navigation pointer** to the target from a file the agent already reads (`AGENTS.md` / `CLAUDE.md`, a README, the neighbouring module), or move/rename the target to where agents look first |
| Stale doc | Correct the doc, or delete it when the environment already answers the question (`--help`, `package.json` scripts, config) |
| Automated check | A lint rule, type, test, pre-commit hook, or CI job. Read the repo's existing scripts and CI first: a check that exists but is unwired is the finding |
| Reviewer | A rule in `CODING_STANDARDS.md` or the repo's equivalent, for judgement calls only; mechanical rules get a check |
| Tool economy | Streamline or replace the tool |
| Information access | Widen access: tee a log to a file, grant read-only access to a service |

`AGENTS.md` / `CLAUDE.md` load into every session, so they carry navigation pointers and little else; steering that belongs in standards or a check moves out. Target whichever of the two the repo keeps current, and read it first so a candidate never repeats a line it already has.

### 5. Present the candidates

Present them in chat, most severe first, where severity is total cost across sessions. For each candidate give the fix, the file it touches, the evidence (session and quote), and the cost it would have saved. Close with the scope used: repo paths, agents, session count, and date range. A repo with nothing worth changing gets that said plainly.

Propose only; apply a candidate once the user picks it.
