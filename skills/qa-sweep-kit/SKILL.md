---
name: qa-sweep-kit
description: QA sweep — turn a running web app into verified, evidenced tracker tickets with a team of browser agents (agent-browser), then file them to Jira. Use when asked to QA, dogfood or bug-hunt an app at scale, or to build a ticket corpus for evaluating coding agents.
compatibility: Claude Code only (runs a Workflow). Needs agent-browser, Node 18+, ffmpeg and jq; the sign-in helper is for Clerk and the filing scripts are for Jira.
---

# QA sweep kit

A **sweep** runs the `qa-sweep` workflow: one explorer per area charter drives the running app, a fresh verifier re-reproduces every finding and tries to refute it, and triage dedupes the survivors. This skill is everything around that workflow: an isolated environment, personas, the brief, charters, the reviewed dedupe pass, filing and cost. First run (2026-11): 211 findings → 141 tickets with 720 attachments for about $271.

Read `references/pitfalls.md` before step 2; every item in it cost real time.

## Steps

1. **Goal and tracker.** Know who acts on the tickets and why (developers, or a coding-agent eval corpus), the tracker project, and the budget. Get a personal Jira API token from the user via a secret prompt (the Rovo MCP can't attach files). Done when `GET /rest/api/3/myself` answers 200 and `mypermissions` shows CREATE_ISSUES and CREATE_ATTACHMENTS for the project.

2. **Isolated environment.** Clone the data into a throwaway database, start every service against the copy as detached processes (`nohup … & disown`, PIDs recorded), mirror production's provider settings from its deploy script, and generate edge-case fixtures (images with text in each language, oversized/corrupt/disguised files, odd names). Done when each service answers, one real call per external provider succeeds, and nothing points at production data.

3. **Personas.** Create test users through the auth provider's admin API: an owner with rich data, a second user/attacker, a no-permission user, and one user per agent that mutates data or spends a per-user quota. Wire a sign-in helper (`scripts/clerk-signin.sh` for Clerk). Done when every persona signs into a fresh `agent-browser` session through the helper.

4. **Brief and existing issues.** Export the tracker's issues to a TSV (key, type, status, summary). Fill `templates/BRIEF.md` for this app: environment table, local quirks that are not bugs, personas, data partitions, quotas. Done when the brief has no `<placeholder>` left and the TSV row count equals the tracker's issue count.

5. **Charters.** Pick areas from `references/charters.md`, adapt each to the app's real routes and files, and give every mutating area its own user or id partition and an upload/paid-call budget. Done when no two areas can mutate the same data.

6. **Run.** Start the workflow by the name your skill list gives it (`alavreniuk-skills:qa-sweep` from the plugin, `qa-sweep` from `~/.claude/workflows/`), with `args` as a JSON object, not a string:
   ```js
   Workflow({ name: 'alavreniuk-skills:qa-sweep', args: {
     brief, existingIssues, evidenceRoot, areas: [{ key, title, charter, users, exploreUploads, verifyUploads }],
     models: { explore: 'haiku' },   // per area tiering: run two sweeps, see "Model tiers"
     idPrefix: 'run2-', sessionPrefix: 'qa', verify: true, triage: true } })
   ```
   Keep the servers alive for the whole run. Done when the workflow returns and its result is saved to disk.

7. **Reviewed dedupe.** Read every ticket title; find same-root-cause groups across areas (same file/function in `developer_notes`, the same symptom on desktop and mobile) and verdict conflicts between runs. Write a plan (`{merges, titles, related_new}`) and apply it with `scripts/merge.mjs`. Spot-check the evidence of every critical and major ticket. Done when no two tickets share a root cause and every evidence path exists.

8. **File.** `scripts/file-jira.mjs` with `JIRA_SITE`, `JIRA_EMAIL`, `JIRA_TOKEN_FILE`, `JIRA_PROJECT`, `QA_LABEL`, `QA_BUILD`: file one ticket with `--only`, check its rendering (inline screenshots, MP4, priority), then the rest; then `scripts/link-related.mjs`. Done when a JQL count on the label (paginated) equals the ledger and no filed ticket lacks attachments.

9. **Cost and cleanup.** `scripts/cost.mjs label=<workflow transcript dir> …` for the spend; stop servers and containers you started, revert tracked files the run modified, delete throwaway worktrees, and report the git state of every repo touched.

## Model tiers

Measured on two coverage areas (gallery/search and accessibility) of the first run, Opus 5.5 verifiers throughout:

| Explorer | Area cost | Real problems surfaced | $ per problem | Explorer precision |
|---|---|---|---|---|
| Opus 5.5 | $31.62 | 44 | $0.72 | 97% |
| Sonnet 5.5 | $22.76 | 31 | $0.73 | 81% |
| Haiku 5.5 | $8.92 | 31 | $0.29 | 69% |

- **Coverage areas** (browse, a11y, settings, mobile browse): Haiku explorers. They surface problems at ~2.5x lower cost; their extra false positives are what the verifier is for.
- **Judgment areas** (security, state/concurrency, AI, API, bulk): Opus explorers until a cheaper tier is measured there.
- **Verifiers and triage: Opus.** With Haiku explorers the verifier becomes most of the bill, and verdicts already vary between runs on borderline findings; settle conflicts in step 7.
- Sonnet buys little: its cache reads cost the same as Opus, and cache reads are ~62% of a sweep. Halving context per call (compact snapshots, notes files) saves more than any model swap.
