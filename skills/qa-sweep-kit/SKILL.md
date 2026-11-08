---
name: qa-sweep-kit
description: QA sweep — turn a running web app into verified, evidenced Jira tickets with a team of browser agents (agent-browser).
disable-model-invocation: true
compatibility: Claude Code only (runs a Workflow). Needs agent-browser, Node 18+, ffmpeg and jq; the bundled sign-in helper is for Clerk (other auth providers need one with the same arguments) and the filing scripts are for Jira.
---

# QA sweep kit

A **sweep** runs the `qa-sweep` workflow: one explorer per area charter drives the running app, a fresh verifier re-reproduces every finding and tries to refute it, and triage dedupes the survivors. This skill is everything around that workflow: an isolated environment, personas, the brief, charters, the reviewed dedupe pass, filing and cost. First run (2026-11): 211 findings → 141 tickets with 720 attachments for about $271.

`<skill>` below is this file's folder.

## Steps

1. **Goal and tracker.** Know who acts on the tickets and why (developers, or a coding-agent eval corpus), the tracker project, and the budget. Get a personal Jira API token from the user via a secret prompt: the Rovo MCP can't attach files, and the scripts send basic auth with the account email, which a service-account token (`ATSTT…`, Bearer auth on `api.atlassian.com`) does not accept. Done when `GET /rest/api/3/myself` answers 200 and `mypermissions` shows CREATE_ISSUES and CREATE_ATTACHMENTS for the project.

2. **Isolated environment.** First check which database the app resolves locally: an unset `*_DEV` URL can fall back to production. Clone the data into a throwaway database and point every service at the copy through a process environment variable, so no env file changes. Start each service as a detached process (`nohup … >> log 2>&1 < /dev/null & disown`, PIDs recorded), because `run_in_background` tasks die after 2 hours. Mirror production's provider settings from its deploy script, and generate edge-case fixtures (images with text in each language, oversized/corrupt/disguised files, odd names). Done when each service answers, one real call per external provider succeeds, and nothing points at production data.

3. **Personas and sign-in.** Create test users through the auth provider's admin API: an owner with rich data, a second user/attacker, a no-permission user, and one user per agent that mutates data or spends a per-user quota. Then write `qa-signin`, the command the brief and the agents call: `qa-signin <session> <user|anon> [start-path]` signs that `agent-browser` session in as the persona (`anon` signs it out), opens `start-path`, and exits non-zero unless the sign-in took. Every Bash call starts a fresh shell, so an `export` or `PATH` change made during setup never reaches the agents: make `qa-signin` an executable wrapper at an absolute path that sets the provider script's environment and `exec`s it, and give that path in the brief.
   - **Clerk:** the wrapper exports `QA_BASE_URL`, `QA_USERS` (a JSON file mapping each persona to its user id) and `CLERK_SECRET_KEY` (read from a file when the wrapper runs, so the wrapper holds no key), then runs `exec <skill>/scripts/clerk-signin.sh "$@"`. A user with no email, username or phone fails with "doesn't have an associated identification"; on an OAuth-only instance the owner must enable an identifier such as Username, which then shows on every app using that instance, so say so when you ask.
   - **Other providers:** write a script with the same arguments and exit status against the provider's admin API (a sign-in or impersonation token), and a wrapper that sets its environment.

   Done when every persona signs into a fresh `agent-browser` session through `qa-signin` and `anon` signs one out.

4. **Brief and existing issues.** Export the tracker's issues to a TSV (key, type, status, summary). Fill `templates/BRIEF.md` for this app: environment table, local quirks that are not bugs, personas, data partitions, quotas. Done when the brief has no `<placeholder>` left and the TSV row count equals the tracker's issue count.

5. **Charters.** Pick areas from `references/charters.md`, adapt each to the app's real routes and files, and give every mutating area its own user or id partition and an upload/paid-call budget. Done when no two areas can mutate the same data.

6. **Run.** Start the workflow by the name your skill list gives it (`alavreniuk-skills:qa-sweep` from the plugin, `qa-sweep` from `~/.claude/workflows/`), with `args` as a JSON object, not a string:
   ```js
   Workflow({ name: 'alavreniuk-skills:qa-sweep', args: {
     brief, existingIssues, evidenceRoot, areas: [{ key, title, charter, users, exploreUploads, verifyUploads }],
     models: { explore: 'haiku' },   // per area tiering: run two sweeps, see "Model tiers"
     idPrefix: 'run2-', sessionPrefix: 'qa', verify: true, triage: true } })
   ```
   Keep the servers alive for the whole run. Done when the workflow returns and its result is saved to disk. If its `triage_status` is `failed`, step 7 also does triage's work: drop findings an open issue in the TSV already covers, and calibrate severity against the brief's scale.

7. **Reviewed dedupe.** Triage misses same-root-cause duplicates across areas: on the first run it merged 17 and this pass 40 more. Read every ticket title and the result's `rejected_merges`; find same-root-cause groups across areas (same file/function in `developer_notes`, the same symptom on desktop and mobile) and verdict conflicts between runs. Write a plan (`{merges, titles, related_new}`) and apply it with `node <skill>/scripts/merge.mjs <tickets.json> <plan.json> <out.json>`. Spot-check the evidence of every critical and major ticket. Done when no two tickets share a root cause and every evidence path exists.

8. **File.** `node <skill>/scripts/file-jira.mjs <tickets.json> <ledger.json>` with `JIRA_SITE`, `JIRA_EMAIL`, `JIRA_TOKEN_FILE`, `JIRA_PROJECT`, `QA_LABEL`, `QA_BUILD`: file one ticket with `--only`, check its rendering (inline screenshots, MP4, priority), then the rest; then `node <skill>/scripts/link-related.mjs <tickets.json> <ledger.json>`. Each exits 1 and names what it left undone (a ticket with no evidence file, a failed link); fix the cause and rerun, and the ledger skips what already went through. Done when both exit 0, a JQL count on the label (paginated) equals the number of tickets in `<tickets.json>`, and no filed ticket lacks attachments.

9. **Cost and cleanup.** `node <skill>/scripts/cost.mjs <label>=<workflow transcript dir> …` for the spend. Stop the servers and containers you started, and the container runtime if it was stopped before (starting OrbStack or Docker Desktop also restarts the user's other containers); revert tracked files the run modified (Next.js `next dev` appends to `AGENTS.md` on every start); delete throwaway worktrees. Done when no PID recorded in step 2 is still running, `git status` in every repo you touched shows only changes the user wants kept, and your report gives the spend, the token counts of every model `cost.mjs` lists under `unpriced`, and the git state of each repo.

## Model tiers

Measured on two coverage areas (gallery/search and accessibility) of the first run, Opus 5.5 verifiers throughout:

| Explorer | Area cost | Real problems surfaced | $ per problem | Explorer precision |
|---|---|---|---|---|
| Opus 5.5 | $31.62 | 44 | $0.72 | 97% |
| Sonnet 5.5 | $22.76 | 31 | $0.73 | 81% |
| Haiku 5.5 | $8.92 | 31 | $0.29 | 69% |

- **Coverage areas** (browse, a11y, settings, mobile browse): Haiku explorers. They surface problems at ~2.5x lower cost; their extra false positives are what the verifier is for.
- **Judgment areas** (security, state/concurrency, AI, API, bulk): Opus explorers until a cheaper tier is measured there. Some security turns are served by the refusal fallback (Opus 4.8), which `cost.mjs` has no price for and lists under `unpriced`.
- **Verifiers and triage: Opus.** With Haiku explorers the verifier becomes most of the bill, and verdicts already vary between runs on borderline findings; settle conflicts in step 7.
- Sonnet buys little: its cache reads cost the same as Opus, and cache reads are ~62% of a sweep (the average call carried ~184K tokens of context). Halving context per call (compact snapshots, notes files) saves more than any model swap.
