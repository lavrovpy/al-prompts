# <PROJECT> QA sweep — shared brief (read fully before testing)

## Goal

<One paragraph: why these tickets exist and who acts on them.> Every ticket must be:

- **real**: the defect or gap exists in the current code, not in this test environment;
- **reproducible**: someone with a fresh local setup can follow the steps and see it;
- **evidenced**: screenshots and/or a screen recording (or a request/response log for API issues) that show it;
- **solvable and checkable**: clear expected behaviour and acceptance criteria.

## Environment (already running — never start, stop, restart, install, build, or edit code in the repos)

| What | Where | Notes |
|---|---|---|
| <web app> | http://localhost:<port> | Code: `<abs path>`, commit `<sha>`. Server log: `<abs path>` (shared by all agents). |
| <API/backend> | http://localhost:<port> | Code, contract (`openapi.yaml`?), auth header and where its value lives (never paste secrets into evidence; write `$VAR`). |
| <database copy> | `<psql command>` | Read freely to confirm state. **Never write to it directly** — change data only through the app or API, as a user would. |

**Local-environment differences (not product bugs — do not file):** <dev-mode overlays, auth-provider dev badges, model or provider substitutions, anything caused by local .env values>.

## Test users

Sign a browser session in with:

```bash
<abs path>/qa-signin <session> <user> [start-path]   # "anon" signs the session out
```

| user | permissions | data it owns | purpose |
|---|---|---|---|
| <user> | <...> | <ids / counts> | <owner / second user / attacker / no-permission / per-agent isolation> |

## Rules for shared data (several agents run at the same time on the same database)

- Use only the user(s) your charter assigns; settings toggles belong to one agent each.
- <Id partitions per mutating agent.>
- Things you create: prefix names with `QA-<your area>-`.
- <Quotas and budgets: uploads per user per day, paid API calls.>
- Dataset quirks that are **not** bugs: <duplicate copies, legacy rows, seed photos that aren't real content>.

## Browser

- Use `agent-browser` only, always with your own `--session <name>` (given in your charter). Close your session when done; never close other sessions. `agent-browser skills get core` has the command reference.
- Desktop: `set viewport 1440 900`. Mobile: `set device "iPhone 14"` (also `"Pixel 7"`, `"iPhone SE"`); confirm with `eval "innerWidth"`.
- Useful: `snapshot -i -c` (refs, compact), `screenshot [--full] [--annotate] <path>`, `errors`, `console`, `network requests --filter …`, `network route <url> --abort`, `set offline on|off`, `eval <js>`.

### Evidence protocol (every finding needs evidence)

Evidence directory: given in your charter — name files `<finding-id>-<short-slug>-<n>.png|webm|txt`.

- **Interactive bugs → video + screenshots.** `record start <path>.webm` opens a *fresh, signed-out browser context*, so the order is: `record start` → (`set device …` if mobile) → `qa-signin <session> <user> <start-path>` → the steps at human pace (`sleep 1` between actions) → screenshot the broken state → `record stop`. Keep videos under ~60 s.
- **Static/visual bugs → screenshot(s)**; for layout bugs put the viewport in the caption.
- **API/backend bugs → a `.txt` log** with the exact `curl` commands and full responses, secrets redacted.
- **Performance → numbers** (how measured, values, repeat count).
- Before reporting a finding, look at your own screenshot to confirm it shows the problem.

## What counts as a finding

- Bugs: functional, UI/visual, data integrity, error handling, security/privacy, accessibility, performance, mobile-specific, API-contract mismatches.
- Missing or incomplete features the UI implies or a reasonable user expects → `issue_type: Story`.
- Performance problems or tech debt with measurable impact → `issue_type: Task`.
- Not findings: local-environment issues (above), pure taste, anything you could not reproduce at least twice (mark one-offs `reproducibility: once` only with unambiguous evidence).

## Existing tickets — don't re-file them

`<abs path>/existing-issues.tsv` lists the existing issues (key, type, status, summary). Grep it before reporting. If an **open** issue already describes your observation, put it in `already_tracked` (key + what you saw + evidence path) instead of `findings`. A materially different aspect → new finding with the key in `related_existing`. Done issues that are broken again are regressions — report them as new findings and say so.

## Writing a finding

- **title**: the user-visible symptom, specific, ≤ 90 characters. Good: "Renaming a meme to spaces saves it and leaves a blank card title". Bad: "Validation bug in EditableField".
- **steps**: numbered, from a known starting point (URL + who is signed in), data-agnostic: describe the precondition ("an image you own that is in an album"), ids only as examples. A developer on a fresh seed must be able to follow them.
- **expected / actual**: concrete, with exact UI text and error messages.
- **evidence**: absolute paths + one-line captions.
- **developer_notes** (optional): facts verified in code, as `path:line` plus one sentence — a hint, not a prescribed fix.
- **acceptance_criteria**: 2–5 testable statements.
- **severity**: critical = data loss, privacy/security leak, or app unusable; major = core feature broken, no workaround; minor = partly broken, workaround exists, or cosmetic with real impact; trivial = polish.
- One problem per finding; one root cause with two symptoms is one finding that names both.
