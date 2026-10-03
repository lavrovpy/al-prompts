# How to apply fixes

Each recipe uses the tool's own CLI where one exists and lists the trap that bit a previous run.

## Claude Code

- **Plugins.** `claude plugin uninstall <plugin>@<marketplace>`. Updates: `claude plugin marketplace update <m>`, then `claude plugin update <p>@<m>` (takes effect on restart). Auto-update: set `"autoUpdate": true` under `extraKnownMarketplaces.<m>` in `~/.claude/settings.json`.
- **Marketplaces.** `claude plugin marketplace remove <m>`, then delete the same name from `extraKnownMarketplaces`, or it is re-added.
- **MCP servers.** `claude mcp remove "<name>" -s user` (or `-s project` / `-s local`), then `claude mcp list` to confirm.
- **`settings.json`.** Load, modify, and dump it with Python, then validate it with `json.load`. Copy it to `~/.claude/backups/` first.
- **`~/.claude.json`.** Running sessions write to it constantly. Copy it to `~/.claude/backups/` (mode 600), then load it, modify it, and replace it atomically (`tempfile` in the same directory plus `os.replace`).

## Skills

- **Skills CLI.** It runs non-interactively when it detects an agent.
  - `npx -y skills remove -g -y <name>` takes one name per call; several names in one call can silently remove only some of them.
  - `npx -y skills update -g -y` updates everything recorded in `~/.agents/.skill-lock.json`.
  - `npx -y skills add <owner/repo> -g -a <agent> -s <name> -y` installs from source; `--list` previews what a repo holds.
- **Move a personal skill to the canonical location:** `mv ~/.claude/skills/X ~/.agents/skills/X && ln -s ../../.agents/skills/X ~/.claude/skills/X`. When the skill's source is a repo, make `~/.agents/skills/X` a symlink to the repo folder instead.
- **After any removal,** sweep for broken links: Pi, Gemini/Antigravity, Cursor, OpenCode, Copilot, `~/.claude/skills`, `~/.agents/skills` (`inventory.py --section tools`).
- **Skills a delegating skill depends on** must stay model-visible: remove the `"off"` override, or set `user-invocable-only` only for skills nothing else calls.

### Repo-local skills that stay uncommitted

1. Put the skill in `<repo>/.agents/skills/<name>`, or `.claude/skills/` when the repo has no `.agents`.
2. Add its path to `<repo>/.git/info/exclude`. That file is shared by every worktree; `.gitignore` is per-branch.
3. Untracked files do not reach other worktrees. Link the skill (and any `settings.local.json`) into each existing worktree from `git worktree list --porcelain`, and never overwrite a real file. Exclude the linked `settings.local.json` too, because older branches may not ignore it.
4. Confirm `git -C <worktree> status --short` is clean in every worktree.
5. Rewrite paths inside the skill that pointed at its old global location (`~/.claude/skills/<name>/scripts/…` becomes repo-relative).

### Validating a skill or marketplace repo

- `claude plugin validate --strict <marketplace-root>` checks the manifest, names, and sources, but not skill frontmatter YAML.
- `uvx --from 'git+https://github.com/agentskills/agentskills#subdirectory=skills-ref' skills-ref validate <skill-dir>` catches frontmatter that standard YAML parsers reject (an unquoted `: ` in a description). It also flags Claude Code-only fields (`argument-hint`, `disable-model-invocation`, `user-invocable`, `arguments`), which are valid in Claude Code.
- End-to-end: `CLAUDE_CONFIG_DIR=$(mktemp -d)`, then `claude plugin marketplace add <root>`, `claude plugin install <p>@<m>`, and `claude plugin details <p>` lists the skills that actually loaded, without touching the real config.

## Codex

- **Auto mode** (CLI equivalent: `--approve-for-me`):
  ```toml
  approval_policy = "on-request"
  sandbox_mode = "workspace-write"
  approvals_reviewer = "auto_review"
  ```
  Put these top-level keys before the first `[table]`.
- **Editing `config.toml`.** Edit it as text with Python, dropping whole `[table]` blocks up to the next header. Validate with `python3 -c 'import tomllib; tomllib.load(open(P,"rb"))'`, then `codex mcp list`, which fails on an invalid config.
- **HTTP MCP with OAuth:** `url = "…"` with no key, then the user runs `codex mcp login <name>`. Context7's OAuth endpoint is `https://mcp.context7.com/mcp/oauth`; plain `/mcp` expects a bearer key.
- **Global instructions** live in `~/.codex/AGENTS.md`. A symlink to `~/.claude/CLAUDE.md` gives Codex the same rules.
- **Rules** are `~/.codex/rules/default.rules`. Back it up, then rewrite it keeping only generic prefixes (test, lint, build, read-only git).

## Cursor

- **MCP servers:** `~/.cursor/mcp.json`. Plugins under `~/.cursor/plugins/cache/` may already provide a server (check their `.mcp.json`).
- **CLI permissions:** `~/.cursor/cli-config.json`. `Shell(cmd)` matches the first token only; narrow it with the `command:args` glob form, e.g. `Shell(git:status*)`. Deny beats allow.
- **Extensions:** `cursor --install-extension <id> --force` updates one.

## VS Code (and Insiders)

- **MCP config:** the user file is `User/mcp.json`; per-profile files are `User/profiles/<id>/mcp.json`. Profile names live in `User/globalStorage/storage.json` → `userDataProfiles`.
- **HTTP MCP with OAuth:** `{"type": "http", "url": "…"}`. Drop the matching `inputs` entry when a key prompt is no longer needed.
- **Extensions:** `code-insiders --update-extensions`, then `--profile "<name>" --update-extensions` for each profile.
- **Orphaned extension folders:** delete them only after confirming no profile's `extensions.json` lists that exact version.

## Packages and binaries

- **npm with several global prefixes:** `npm ls -g` shows one prefix only. For packages under another, run `npm rm -g --prefix /opt/homebrew <pkg>` (or `i -g … @latest` to update).
- **brew:** `brew uninstall <formula>`, then `brew untap <tap>` when no installed formula or cask still comes from it.
- **gh extensions:** `gh extension remove <name>`.
- **Duplicate installs:** keep the first on `which -a <bin>` and remove the other with the method that installed it.
- **Keep the history when uninstalling.** Delete the binary, credentials, and caches, and leave the tasks/threads/sessions folders.

## Shell traps

- zsh aborts the whole command line on an unmatched glob. Use `find <dir> -maxdepth 1 -name '<glob>' -delete` for optional files.
- zsh does not word-split `$VAR`. Loop over a Python list, or use `${=VAR}`.
- macOS `sed -E` has no `\s`, so masking regexes silently match nothing. Mask in Python.
- Leak-check before reading generated output: run the token regexes from `inventory.py` (`SECRET_PREFIXES`) over the file.
