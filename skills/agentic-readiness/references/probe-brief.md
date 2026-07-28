# Agent briefs

Four agents run per assessment. Copy these templates, substitute the bracketed
values, and change nothing else. The wording is load-bearing: three of the four
agents must never learn that a readiness assessment is happening.

**Substitutions used below**

| Token | Meaning |
| --- | --- |
| `[TASK]` | The ticket text, verbatim |
| `[REPO]` | Absolute path of the repository under assessment |
| `[JOURNAL]` | Absolute path in the scratchpad for the probe's work log |
| `[BUDGET]` | Tool-call budget, default 150 |
| `[QUESTION]` | One blind verification question |
| `[BRANCH]` | The probe's branch or worktree path |

---

## 1. The probe

Spawn with **exactly** these parameters:

```
subagent_type: "general-purpose"     # never "fork" — a fork inherits this
                                     # conversation and already knows the repo
model: "sonnet"                      # pinned; see SKILL.md on instrument sensitivity
isolation: "worktree"                # fresh checkout, cold start
name: "readiness-probe"              # required — makes the transcript findable
```

### Prompt

> You are picking up a ticket on a codebase you have not worked on before. You
> are working in a fresh checkout at `[REPO]` — treat it as a clean machine.
>
> **Ticket**
>
> [TASK]
>
> **Definition of done**
>
> 1. The feature is actually implemented — not stubbed, not sketched.
> 2. Whatever validation this project uses for a change like this passes. Find
>    out what that is and run it. A change nobody verified is not done.
> 3. Your work is committed, following whatever commit conventions this project
>    uses.
>
> **Working notes**
>
> Keep a running work log at `[JOURNAL]`, appending as you go. This is normal
> practice here so someone else can pick the work up mid-flight. For each entry
> record the time, what you were trying to do, what you did, and how it turned
> out. When you needed to find something out — where a thing lives, how to run
> something, which pattern to follow — note what you searched for and where the
> answer actually turned out to be.
>
> **Budget**
>
> You have roughly [BUDGET] tool calls. If you get low, stop adding scope:
> verify what you have built and commit it rather than leaving it unfinished.
>
> **If you get stuck**
>
> Work it out yourself where you reasonably can — do not ask for confirmation on
> decisions that are yours to make. But if you hit something you genuinely cannot
> resolve from the repository itself, message the coordinator (`SendMessage` to
> `coordinator`) saying precisely what you need. Do that rather than guessing on
> something load-bearing or burning your whole budget on one wall.
>
> Report back when done: what you built, what you ran to verify it, and the
> commit(s) you made.

### Rules for the coordinator while the probe runs

- Answer hint requests **minimally** — the smallest true answer that unblocks,
  no tour of the architecture. Then log the request as a P0 finding.
- Never volunteer information the probe did not ask for.
- Never hint that the run is being measured.

---

## 2. The debrief

Sent to the **same** probe via `SendMessage` after it reports done. Load
`SendMessage` first with `ToolSearch("select:SendMessage")`. Its context still
holds the whole experience, so this is where the richest material comes from —
and because the work is already recorded, nothing it says now can distort the
behaviour being measured.

### Prompt

> Thanks — that is the implementation done. Now a retrospective, which is
> genuinely the more valuable half of this exercise. We are trying to make this
> repository easier for a newcomer to work in, and you have just been the
> newcomer. Be blunt; there is no credit here for having found things easy.
>
> 1. **Every point you were stuck for more than a couple of minutes.** What were
>    you trying to find out, what did you try, and where did the answer finally
>    turn out to be? Include the ones you eventually solved.
> 2. **Every question you wanted to ask a human but worked around instead.**
>    Even small ones. Especially the ones where you picked an option and moved on.
> 3. **Everything you guessed at** because the repository did not tell you —
>    naming, file placement, which test layer, error handling style, commit
>    format. Say how confident you actually were.
> 4. **Anything you had to run that felt unusual, privileged, or risky** — a
>    download, an install from outside a package manager, something touching
>    files outside the repo, anything you would hesitate to run unattended.
> 5. **What single file, with what content, would have saved you the most time?**
>    Name the path and draft the actual text.
> 6. **What was genuinely easy?** Name what the repo already does well, so we do
>    not waste effort rewriting things that work.

---

## 3. Blind verifiers

One per candidate finding, spawned in parallel. Each gets a **question**, never
the probe's claim — an agent told the conclusion goes looking for evidence to
support it. Each must be a fresh `general-purpose` agent on **`sonnet`**: the
same model as the probe, or the cost comparison is meaningless.

Do not name them `readiness-*`; do not mention audits, probes, or measurement.

### Prompt

> You are new to the repository at `[REPO]`. Answer this question using at most
> **10 tool calls**:
>
> [QUESTION]
>
> Reply in exactly this form:
>
> ```
> ANSWER: <the answer, or NOT_FOUND>
> SOURCE: <file:line that told you, or "inferred from <path>", or NONE>
> CALLS_USED: <integer>
> CONFIDENT: <yes|no>
> ```
>
> If you cannot answer within 10 tool calls, reply `ANSWER: NOT_FOUND` with the
> calls you used. Not finding it is a perfectly acceptable outcome — do not
> guess to fill the field.

### Turning a claim into a question

Strip the conclusion, keep the information need. The question must be answerable
without knowing the probe ever existed.

| Probe claim | Verifier question |
| --- | --- |
| "No documented way to run the tests" | "What command runs this project's test suite?" |
| "Took ages to find where HTTP routes are registered" | "Where are HTTP routes registered in this project?" |
| "Had to guess the test file location" | "Where does a test for a new module belong, and what is the naming convention?" |
| "Bootstrap needed an undocumented second command" | "What is the complete set of commands needed to get this repo runnable from a clean checkout?" |

---

## 4. The diff reviewer

One fresh `general-purpose` agent on **`sonnet`**. Catches the failure the probe
cannot self-report: confident, silent non-conformance. Give it the diff location
and nothing about the probe.

### Prompt

> A contributor new to this repository produced the change on `[BRANCH]`. Review
> it for **convention conformance only** — not correctness, not code quality.
>
> First, work out independently what this repository's actual conventions are for
> the areas the change touches: file placement, naming, test location and style,
> error handling, commit message shape, and the order commits are expected to land
> in. Derive them from the existing code and docs.
>
> Then list every place the change deviates. For each deviation report:
>
> ```
> DEVIATION: <what the change did>
> CONVENTION: <what this repo actually does>
> DOCUMENTED_AT: <file:line stating the convention, or NOT_DOCUMENTED>
> HOW_A_NEWCOMER_WOULD_KNOW: <the shortest path to discovering it, or "they wouldn't">
> ```
>
> `DOCUMENTED_AT: NOT_DOCUMENTED` combined with a real deviation is the most
> important thing you can find — report those even when the deviation is minor.
> If the change conforms throughout, say so plainly.
