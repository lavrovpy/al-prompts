# What to look for

Each check names the evidence that proves it and the usual fix. `inventory.py` already surfaces the items marked *(script)*.

## Usage evidence

Judge "unused" from records, not impressions:

- `~/.claude.json`: `skillUsage`, `pluginUsage` (counts and `lastUsedAt` ms timestamps) *(script)*. `toolUsage` undercounts; treat it as a hint.
- Real MCP calls: transcripts under `~/.claude/projects/**/*.jsonl` containing `"type":"tool_use","id":"…","name":"mcp__<server>__…"` *(script)*. A bare `"name":"mcp__…"` also matches the deferred-tool listing that every session records, so it overcounts.
- Last activity: newest mtime in the tool's directory *(script)*; for a skill, its `SKILL.md` mtime plus usage.
- A CLI that replaced an MCP server (e.g. `glab` for a GitLab MCP) shows up as a skill with recent usage.

## Security

- **Blanket allow rules.** Codex `~/.codex/rules/*.rules` with `prefix_rule(pattern=["/bin/zsh"])`: Codex runs commands as `/bin/zsh -lc …`, so it matches everything *(script)*. Interpreter rules (`uv run python`, `node`) and `git push` are just as broad. Cursor CLI `Shell(git)` allows every git subcommand. Fix: delete them, and give Codex auto mode instead (RECIPES § Codex).
- **Project rules in user scope.** Claude `permissions.allow` entries naming one project's commands move to that repo's `.claude/settings.local.json`.
- **Broad trust.** Codex `[projects."<path>"]` for `~`, `~/Desktop`, `~/Downloads`, plus deleted or empty folders *(script)*.
- **Plaintext secrets** *(script)*: world-readable modes (644), copies in `.bak` files, the same secret in several tools' MCP configs, and keys passed as command args (visible in `ps`). Every MCP config that embeds a credential is one more copy to rotate.
- **Write-capable MCP under auto mode.** Approve, merge, and admin tools reachable without a prompt need a deny list, or the server goes when a CLI has replaced it.
- **Third-party hooks.** Hook files installed by vendor skill packs (e.g. `~/.agents/hooks/hooks.json`) that run on every tool call.

## Broken or contradicting

- **`skillOverrides: "off"`** hides a skill from the user *and* the model, so any skill that delegates to it breaks *(script lists the chains)*. For "only I invoke it" the value is `user-invocable-only`.
- **Invalid settings keys.** Compare `~/.claude/settings.json` keys with `https://json.schemastore.org/claude-code-settings.json`. `mcpServers` there is dead config. Schemastore lags new keys, so an absent key is a question for the docs, not proof it is invalid.
- **Steering that fights the user's instructions.** Output-style plugins inject text at every SessionStart; compare it with CLAUDE.md (a "learning" style that asks the user to write code contradicts "finish the work"). Two style plugins can inject overlapping text twice.
- **Dead servers.** The command is missing (`which`), the URL fails (`curl -X POST` gives 404), or the entry is disabled.
- **Drifted copies** of one skill (a global copy vs. the repo's committed one).

## Per-session context cost

- **Model-visible skills.** Each description loads every turn; `disable-model-invocation: true` skills cost nothing until invoked.
- **User-scope plugins.** Count their skills, agents, and hooks (`claude plugin details <p>`). Measure a SessionStart hook's injected text by running its script and counting characters.
- **MCP servers.** Each adds its tool names to the deferred list and a process at startup; one with zero real calls is pure cost.
- **Codex** loads every skill in `~/.agents/skills` and `~/.codex/skills`, so vendor packs installed for one tool load in Codex too.

## Provenance

A skill copied from a marketplace drifts from upstream and never updates. For each real-directory skill:

1. Run `npx -y skills find <name>` and keep results whose `owner/repo@<skill>` part equals the name exactly.
2. Shallow-clone each candidate repo and run `diff -rq` against the local folder. Identical means a marketplace copy; reinstall it from source (RECIPES § Skills). A different body under the same name means it is the user's own skill.
3. Before treating a personal skill's local copy as the original, look for the user's own skill repos (a prompt library, a course repo). When one holds the skill, the local entry becomes a symlink to the repo.

## Layout and duplication

- **Canonical layout.** Real skills, or symlinks to their source repos, live in `~/.agents/skills`. `~/.claude/skills/<name>` → `../../.agents/skills/<name>`. `~/.codex/skills` holds only `.system`, because Codex reads `~/.agents/skills` directly and a second copy loads twice.
- **Project-specific skills living globally** move into that repo's `.agents/skills`; RECIPES covers keeping them uncommitted.
- **Broken symlinks** in any agent skill directory *(script)*, typically left behind after a removal.

## Staleness

- Marketplaces without auto-update, and plugin versions behind upstream.
- Unpinned `@latest` / versionless npx MCP servers *(script, for Codex)*; pin them to `npm view <pkg> version`.
- An IDE extension version behind the CLI version of the same tool.
- Two installs of one tool (brew and a curl script): keep the one first on `which -a`.
- Global npm installs that are not on PATH, under a second npm prefix.

## Disk and leftovers

- Data folders of uninstalled apps, old binaries, logs, `*.tmp` and `*.bak` files, skill `.trash` folders.
- **Orphaned extension versions.** Confirm against every profile's `extensions.json` by exact version: a substring grep for `2026.3.1` also matches `2026.3.100`.
- Plugin caches of uninstalled Claude plugins get `.orphaned_at` markers and Claude Code collects them itself; leave them.

## Subagent prompt

Fill in the scope (the paths or tools) and send one per scope:

> Read-only audit of <scope> on macOS. Change nothing. Report a secret as "present" with its key name, never its value. For chat or session history, report only file counts, total size, and the newest modification date. For each item, establish: installed (`which`, `/Applications`, brew/npm lists), last activity (newest mtime), size (`du -sh`), the MCP servers, rules, skills, agents, and hooks it configures, duplicates of skills in `~/.agents/skills` or `~/.claude/skills`, broken symlinks, plaintext secrets with file modes, unpinned `@latest` servers, and servers whose binary or URL is dead. Return a table (Tool | Installed | Last activity | Size | Notable config) and recommendations tagged DELETE / UPDATE / CHANGE / KEEP, each with the exact path and observed evidence. Mark every path that holds chat history as KEEP.
