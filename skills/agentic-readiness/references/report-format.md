# Report format

## The spine

Findings are filed into a fixed spine so runs stay comparable. The probe is never
shown this list — discovery is emergent, and the spine is applied afterwards.

| Phase | Covers |
| --- | --- |
| **Bootstrap** | Clean checkout to runnable: install, native deps, env vars, services, credentials |
| **Orient** | Grasping the architecture: what the parts are, which layer owns what, which rules are non-negotiable |
| **Locate** | Finding the exact files this change touches |
| **Change** | Writing code that matches existing conventions: placement, naming, error handling, test style |
| **Validate** | Discovering and running the project's own checks, and interpreting failures |
| **Land** | Committing to convention: message shape, commit ordering, branch policy, PR expectations |
| **Other** | Anything that fits nowhere above. Do not force-fit |

Each phase gets one verdict:

- **clean** — no confirmed findings
- **friction** — confirmed findings, none blocking
- **blocked** — at least one P0
- **not reached** — the run never got here (say why; the phase is unmeasured, not clean)

No numeric score. A composite number invites gaming and implies precision the
method does not have.

---

## Severity

Anchored on one bar: **a ticket goes in, a merge request comes out, no human
turns in between.** Severity is how badly a finding violates that.

| Level | Meaning | Sources |
| --- | --- | --- |
| **P0** | An unattended agent stops here. Production impact: the run dies and a human is paged | A hint was granted; the probe wanted to ask a question it needed answered; auto mode blocked a required operation; validation was undiscoverable; bootstrap was impossible without tribal knowledge |
| **P1** | The agent proceeds confidently and is wrong. Production impact: a non-conforming MR merges, because nothing flagged it | Diff review found a deviation with `DOCUMENTED_AT: NOT_DOCUMENTED`; the probe guessed at something load-bearing and did not know it was guessing |
| **P2** | The agent gets there, expensively. Production impact: burned tokens and time | Confirmed friction — verifier needed ≥6 calls, or forensics show churn, retries, or long stalls |
| **P3** | Papercut | `PARTIAL` verifier verdicts; minor deviations that are documented but awkward to find |

P1 outranks P2 deliberately. Silent wrongness is worse than expensive rightness —
expensive rightness shows up in a bill, silent wrongness shows up in `main`.

---

## Where a fix belongs

A finding without a named home is a nag. Route by the shape of the knowledge:

| Knowledge shape | Home |
| --- | --- |
| Short invariant relevant to nearly every task | `CLAUDE.md` / `AGENTS.md` |
| Long procedure relevant only sometimes | A skill — `.claude/skills/<name>/SKILL.md` |
| Facts about one directory | `README.md` inside that directory |
| Mechanical and repeatable | A script, plus one pointer line where the agent looked |
| **Enforceable** | A lint rule, CI check, or type — **prefer this over prose** |
| Right code, unfindable | A pointer line placed **where the probe actually searched** |

Two rules that matter more than they look:

**Prefer enforcement to documentation.** Prose rots silently; a failing check does
not. If a convention can be expressed as a lint rule or a test, propose that —
and note that it also removes the need for the doc.

**Put the pointer where the agent looked, not where it "should" be.** The
forensics show which files the probe opened first. A note in the file nobody opens
fixes nothing.

Every fix ships as drafted content, in a fenced block, ready to paste. Never
"document the test command".

---

## Report template

````markdown
# Agentic readiness — <repo> @ <short-sha>

**Task**: "<task>" (<supplied|proposed>)
**Probe**: sonnet, <N> tool calls, <duration>, worktree `<path>`
**Outcome**: <feature completed | partial | blocked at <phase>>
**Verifier thresholds**: found ≤2 = downgrade, 3–5 = partial, ≥6 = confirmed

| Phase | Verdict | P0 | P1 | P2 | P3 |
| --- | --- | --: | --: | --: | --: |
| Bootstrap | | | | | |
| Orient | | | | | |
| Locate | | | | | |
| Change | | | | | |
| Validate | | | | | |
| Land | | | | | |

## Findings

### P0-1 — <one-line title>

**Phase**: <phase>
**What happened**: <what the probe was trying to do, what it tried, how it ended>
**Evidence**: <forensics numbers, journal line, or diff deviation>
**Blind verifier**: asked "<question>" → <ANSWER> in <N> calls, source <SOURCE>. **<CONFIRMED|PARTIAL>**
**Fix** — add to `<path>` (<why this home>):

```
<drafted content, paste-ready>
```

<repeat per finding, P0 first>

## Questions the probe wanted to ask

Each one is a place an unattended run would have stopped.

| Question | How it worked around it | Was the guess right? |
| --- | --- | --- |

## Operations an autonomous agent should not be trusted with

Commands required to build, test or run that auto mode blocked or would block.

| Operation | Needed for | Safer equivalent |
| --- | --- | --- |

## What already works

Do not "improve" these — they measurably carried the run.

## Instrument noise

Harness-caused failures, excluded from all verdicts. Present so the blind spots
in this measurement are visible.

## Dropped findings

Claims the verifiers refuted, with the calls each took. Kept for auditability.
````

---

## Console summary

Print, in chat: the phase table, every P0 and P1 as a one-liner, the count of
P2/P3, and the full report's path. Do not paste the whole report into chat — the
table plus the blockers is the decision-grade part.
