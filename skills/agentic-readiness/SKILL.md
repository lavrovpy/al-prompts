---
name: agentic-readiness
description: This skill should be used when the user asks to "check agentic readiness", "is this repo AI-ready", "is my repository agent-friendly", "why do agents struggle with this codebase", "what's missing for autonomous agents", "audit this repo for AI-first development", "could an agent work here unattended", or invokes "/agentic-readiness". It measures how ready a repository is for autonomous agent development by dispatching a probe agent to genuinely implement a feature in an isolated worktree, then reporting — with evidence — every place the agent was blocked, had to ask, guessed wrong, or wasted effort, along with paste-ready fixes.
argument-hint: "[task description, e.g. 'add another endpoint']"
---

# Agentic readiness

Measures one thing: **can an agent take a ticket and produce a merge request with
zero human turns in between?** Every moment a human had to intervene — a granted
hint, a question the agent needed answered, an undiscoverable test command — is a
defect in the repository, not in the agent.

This is an **experiment, not a checklist**. Nothing here enumerates "does the repo
have a README". A probe agent is sent to do real work, and whatever it struggles
with is, by definition, what needs fixing. Findings are discovered, never
pre-listed; the reporting spine is applied only afterwards.

## The method

| Agent | Role | Knows it is being measured? |
| --- | --- | --- |
| **Probe** (sonnet, worktree) | Implements the ticket for real | **No** — until the post-hoc debrief |
| **Blind verifiers** (sonnet, ×N) | Independently answer the questions the probe struggled with | **No** — ever |
| **Diff reviewer** (sonnet) | Checks the probe's output against real conventions | **No** — ever |
| **Coordinator** (this session) | Grants hints, tallies verdicts, writes the report | — |

Three constraints make the measurement valid. Violating any of them silently
invalidates the run:

1. **The probe must not know it is being measured** while it works. An agent told
   its job is to find friction will manufacture friction and under-invest in
   finishing. It learns the truth only in the debrief, after its behaviour is
   already recorded and can no longer be distorted.
2. **The coordinator must never search the repo to check a claim.** A context
   window that now contains the answer cannot judge how hard the answer was to
   find. Dispatch a blind verifier instead — always.
3. **Verifiers get the question, never the claim.** An agent told the conclusion
   hunts for confirming evidence.

## Pre-flight

1. Confirm a **git repository**, clean enough to branch from. Note the short SHA.
2. Check the session's permission posture. Auto mode is the intended setting: it
   auto-approves reads and in-project edits, and routes everything else to a
   classifier. Under a restrictive mode the probe fights the harness and the run
   is confounded — warn, and offer to continue anyway.
3. State the expected cost in one line (a full run is a bootstrap, an
   implementation, a validation loop, and a verifier fan-out) and proceed. Do not
   block on approval.

## Step 1 — Choose the ticket

If the user supplied a task, use it **verbatim**. Otherwise survey the repo
shallowly — top-level layout, package boundaries, an existing test — and propose
one, stating which and why.

A proposed task must:

- **mirror an existing pattern** — at least one sibling exists to learn from
- **cross ≥2 layers or packages**, so cross-boundary conventions get exercised
- **require a test**, so the validation loop is reached
- **not already be a worked example** in the docs
- be genuinely plausible, and not already implemented

Keep the survey shallow. Deep reading here contaminates the coordinator's context
for exactly the judgement it must make later.

## Step 2 — Run the probe

Spawn per `references/probe-brief.md` §1 — `general-purpose`, `model: "sonnet"`,
`isolation: "worktree"`, `name: "readiness-probe"`.

The model is pinned deliberately. A stronger probe simply *infers* undocumented
conventions correctly and reports no friction where a real gap exists — it is a
less sensitive instrument, and it does not match the cheaper agents that run
unattended. Record the model in the report so runs stay comparable.

Never use `subagent_type: "fork"`. A fork inherits this conversation and already
knows the repository.

## Step 3 — Handle escalations

The probe may message the coordinator when genuinely stuck. For each request:

1. Answer **minimally** — the smallest true answer that unblocks. No architecture
   tour, no volunteered extras.
2. Record it immediately as a **P0** finding, with what the probe tried first.
3. Never hint that the run is being measured.

Each hint converts a fatal blocker into a data point and lets the run continue, so
one probe maps the whole path instead of stopping at the first pothole.

## Step 4 — Debrief the probe

Once the probe reports done, send the retrospective from `references/probe-brief.md`
§2 via `SendMessage` (load it first: `ToolSearch("select:SendMessage")`). This is
the richest single source — the probe's context still holds the entire experience,
and revealing the purpose now cannot retroactively change what it did.

## Step 5 — Transcript forensics

```sh
python3 <skill-dir>/scripts/probe-forensics.py --name readiness-probe
```

Emits wall clock, per-tool call and error counts, repeated searches, re-read
files, the full Bash timeline, and the longest stalls. This is the tiebreaker
channel: the journal says what the probe *felt*, the transcript says what it
actually *did*.

Read `references/evidence.md` for the friction signatures — which patterns mean
"went in circles", which mean "the error message was illegible", and why *no
validation commands at all* is the strongest finding available.

If no transcript is found, say so in the report and proceed on the other two
channels. Never fabricate forensics.

## Step 6 — Verify blind, in parallel

Convert every candidate finding into a neutral **question**, then spawn one fresh
`sonnet` verifier per question, all in a single message so they run concurrently.
Templates and claim→question rewrites: `references/probe-brief.md` §3.

Apply the downgrade rule from `references/evidence.md`: a verifier that finds the
answer in ≤2 calls means the probe was weak, not the repo — **drop the finding**.
Dropping them is the point. A report padded with agent-noise trains the reader to
distrust the whole document.

## Step 7 — Review the diff

Spawn one fresh `sonnet` reviewer against the probe's branch
(`references/probe-brief.md` §4). This catches the failure mode neither other
channel can see: the probe that confidently put the file in the wrong place,
never struggled, and reported nothing.

Any deviation with `DOCUMENTED_AT: NOT_DOCUMENTED` is a **P1** — silent
wrongness, which outranks expensive rightness because it lands in `main` unnoticed.

## Step 8 — Report

Build the report per `references/report-format.md`: phase table with per-phase
verdicts (clean / friction / blocked / not reached), findings ranked P0 first,
each with evidence, verifier verdict, and a **paste-ready fix in a named home**.

Route each fix by knowledge shape — short invariant to `CLAUDE.md`, long procedure
to a skill, enforceable rule to a lint check rather than prose. Put pointers where
the probe **actually searched**, which the forensics reveal.

Write the full report to the session scratchpad and print its path. In chat, print
only the phase table, every P0 and P1 as a one-liner, and the P2/P3 counts.

**Write nothing into the repository under measurement.** Leave the worktree and
branch in place, print the path, and let the user decide when to remove it.

## Guardrails

- **No finding without evidence** — a journal line, a forensics number, a verifier
  verdict, or a diff deviation. Anything else is speculation.
- **Task difficulty is not a defect.** Report only friction that documentation,
  tooling, or structure could have removed.
- **Harness failures are not repo failures.** Denials from local settings, absent
  network, or missing personal credentials go to an "instrument noise" section and
  never affect a verdict. But a classifier block on an operation genuinely
  *required* to build or test **is** a P0: the repo demands something an autonomous
  agent should not be trusted to run. See `references/evidence.md`.
- **Report what already works.** A run that lists only problems reads as a demand
  to rewrite everything, and invites "fixing" the parts that carried the run.
- **Never fix anything.** This skill diagnoses. Applying its own remedies would
  mutate the thing it was hired to measure.

## Resources

- **`references/probe-brief.md`** — verbatim prompts for the probe, debrief,
  blind verifiers, and diff reviewer, plus spawn parameters. The wording is
  load-bearing; substitute the bracketed values and change nothing else.
- **`references/evidence.md`** — friction signatures, the downgrade rule and its
  tunable thresholds, harness-interference classification, analyst guardrails.
- **`references/report-format.md`** — the phase spine, severity ladder, fix-home
  routing table, and the full report template.
- **`scripts/probe-forensics.py`** — transcript locator and forensic summariser.
  Stdlib only, read-only, `--list` / `--name` / `--path`.
