# Pitfalls seen in practice

Each cost real time in the first sweep (2026-11). Check them during setup.

## Environment

- **The dev server may point at production data.** Check which database the app resolves locally before starting it (e.g. an unset `*_DEV` URL falling back to the production one). Clone the data into a throwaway Postgres (`pg_dump` from the source only reads) and point the app at the copy through a process env var, so no env file changes.
- **Background tasks die after 2 hours** in Claude Code (`run_in_background` cap). Start servers the sweep needs with `nohup … >> log 2>&1 < /dev/null & disown`, record their PIDs, and stop them at the end.
- **Stale local secrets.** Revoked LLM keys and wrong base URLs in local `.env` files produce failures that look like product bugs. Smoke-test every external dependency (one real call each) before launching agents; mirror production's provider settings from its deploy script.
- **Starting the container runtime starts other things.** OrbStack/Docker Desktop restarts the user's other containers and clusters; stop it again at the end if it was stopped before.
- **Framework writes tracked files.** Next.js 16.3 `next dev` appends a block to AGENTS.md on every start; revert tracked-file changes the run caused before reporting git state.

## Auth and personas

- **Sign-in tokens need an identifier.** Clerk's `sign_in_tokens` (ticket strategy) and actor tokens fail with "doesn't have an associated identification" when the user has no email/username/phone — instances that only allow OAuth need an identifier (e.g. Username) enabled by the owner. Enabling it shows on every app using that instance; say so.
- **`record start` opens a fresh, signed-out browser context.** Sign in after starting the recording (and re-apply device emulation for mobile).
- **One user per mutating agent.** Upload quotas, settings toggles and preferences are per user; sharing a user across agents produces false "quota exceeded" and flapping-settings findings.

## Agents

- **Context size drives cost.** In the first run ~62% of spend was cache reads: the average call carried ~184K tokens of context because agents accumulated full snapshots, screenshots and logs. Compact snapshots (`snapshot -i -c -s …`), grep/tail instead of full dumps, and notes files cut this for every model tier.
- **Security charters trip safety classifiers.** On Opus 5.5 the security explorer's requests were partly served by the refusal fallback (Opus 4.8). Budget for it; it doesn't block the run.
- **Triage misses same-root-cause duplicates across areas.** The triage agent merged 17 duplicates; a human-reviewed pass merged 40 more (same file/function in developer_notes, same symptom on desktop and mobile). Always do a reviewed dedupe pass before filing (`scripts/merge.mjs` with a plan file).
- **Steps must survive a different dataset.** Whoever fixes the tickets reproduces on seed data, not your copy: steps describe preconditions, ids are examples only.

## Filing (Jira)

- The Atlassian Rovo MCP creates issues but can't attach files; attachments need a personal API token (basic auth with the account email). Service-account tokens (`ATSTT…`) use Bearer auth on `api.atlassian.com/ex/jira/<cloudId>` instead.
- Team-managed projects may still accept `priority` on create; the script retries without it if not.
- Jira previews MP4 reliably; the script converts WebM with ffmpeg. Inline screenshots work by embedding the attachment's Media API file id (from the attachment content redirect) in the ADF description.
- `/rest/api/3/search/jql` returns at most 100 issues per page — paginate (or split by key range) when verifying the filed set.
