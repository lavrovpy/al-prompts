---
name: ai-setup-audit
description: Audit every AI coding tool on this machine (skills, MCP servers, plugins, agents, hooks, configs), rank fixes for the user to approve, apply the approved ones, and report.
disable-model-invocation: true
argument-hint: "[focus, e.g. 'security only' or 'claude code']"
---

# AI setup audit

An **audit** of the machine's AI coding setup: Claude Code, Codex, Cursor, and the long tail of agent CLIs, IDE extensions, and local model runtimes. It runs as **inventory** (read-only), **decisions** (the user rules on each item), **execution** (approved items only), and **report**. The user is the gate between inventory and execution.

A focus argument narrows the inventory; the guardrails and phases stay the same.

## Guardrails

- **History survives.** Session transcripts, threads, task histories, conversation databases, and `history.json(l)` files stay on disk even when their tool is uninstalled. The inventory's "history to keep" column lists the known paths.
- **Secrets stay masked.** Report a secret by file, key name, and file mode. Detect and edit secrets in Python, and leak-check any output file against token patterns before reading it. Shell masking fails quietly: macOS `sed -E` has no `\s`, and zsh does not word-split an unquoted `$VAR`.
- **Symlinks resolve before deletes.** Before removing a directory, find what points into it; a live binary can sit inside a "downloads" or cache folder.
- **Subagent claims get verified.** Each claim that reaches the user was rechecked with a direct command.

## Phase 1: Inventory

1. Run `python3 <this skill's folder>/scripts/inventory.py > "$TMPDIR/ai-inventory.md"` and read the file; add `--no-transcripts` to skip the MCP-call scan. Keep this file: it is the before-snapshot for the report.
2. Dispatch two read-only subagents in one message, using the prompt in [CHECKS.md](references/CHECKS.md#subagent-prompt): one for Codex and Cursor beyond what the script reads, one for the long tail.
3. Check the provenance of every skill that is a real directory, per [CHECKS.md § Provenance](references/CHECKS.md#provenance).
4. Classify each inventory row against [CHECKS.md](references/CHECKS.md) as KEEP, DELETE, UPDATE, or CHANGE, each with its evidence (date, count, size, path).

Done when every row of the snapshot and every subagent finding has a tag and evidence.

## Phase 2: Decisions

Present the findings grouped by tool, ranked: security, then broken or contradicting config, then per-session context cost, then duplication and drift, then disk. Each line carries its tag, the exact path, and one sentence of evidence. Close with the five items you would do first.

Then stop for the user's rulings. An item the user does not mention stays untouched; a "keep" or a pushback is final for this run.

## Phase 3: Execution

Work through the approved items with [RECIPES.md](references/RECIPES.md):

- Use the tool's own CLI (`claude plugin`, `claude mcp`, `npx skills`, `brew`, `npm`, `code --profile`) before editing its files.
- Back up a config before editing it (`<file>.pre-audit`, mode 600, secret values scrubbed), then confirm the edited file parses and the tool loads it.
- Recheck each item right after its change: the listing no longer shows it, the path is gone, `git status` is clean.
- Post a one-line status every few items.

When an approved item turns out unsafe as stated, apply the safe subset and record the deviation.

## Phase 4: Report

1. Run `scripts/inventory.py` again and compare it with the phase-1 snapshot.
2. Report:
   - What changed, per tool.
   - A before/after table: security exposures; per-session context (MCP servers, deferred tool names, injected hook text, model-visible skills); skills layout; disk freed.
   - Deviations from the approved plan, with the reason.
   - Mistakes made during the run, such as a value that reached output.
   - Actions only the user can take: key revocations, OAuth logins, restarts.
   - Items left untouched because they were not approved.
