# Reading the evidence

Three channels, each proving something the others cannot:

| Channel | Proves | Blind to |
| --- | --- | --- |
| **Journal + debrief** | *Why* something was hard, and what would have fixed it | Waste the probe never noticed |
| **Transcript forensics** | *Whether* it was actually hard — counts, retries, stalls | Whether the output was correct |
| **Diff review** | Whether the result *conformed* to unwritten conventions | Effort spent |

A finding supported by only the journal is a claim. A finding corroborated by
the transcript, or produced by the diff review, is evidence.

---

## Getting the transcript

```sh
python3 <skill>/scripts/probe-forensics.py --list
python3 <skill>/scripts/probe-forensics.py --name readiness-probe
```

Transcripts live at `~/.claude/projects/<encoded-cwd>/<session>/subagents/agent-*.jsonl`
with a `.meta.json` sibling holding the agent's name and model. A worktree-isolated
probe may file under its **own** encoded path, so the script searches every project
directory rather than just the current one.

This path is a Claude Code implementation detail, not a public contract. If the
script finds nothing, do not fabricate forensics: proceed on journal and diff
evidence and state in the report that transcript corroboration was unavailable.

---

## Friction signatures

What to look for in the forensics output, and what each implies.

| Signature | Reads as |
| --- | --- |
| Same `Grep`/`Glob` pattern issued 3+ times | Went in circles — the thing being searched for is not where a newcomer expects it |
| Many `Read` calls before the first edit | Expensive orientation; the architecture is not summarised anywhere |
| A file re-read 3+ times | Used as a reference because nothing documents what it establishes |
| Failed command → near-identical retry → success | Trial-and-error against an undocumented interface. Count the tries |
| Long stall right after a validation failure | The error message was not self-explanatory |
| Validation commands appearing only near the end | The feedback loop was hard to discover — everything before it was unverified |
| **No validation commands at all** | The strongest possible finding. The probe could not find how to check its own work |
| Bash touching paths outside the repo | Undocumented environment assumptions |
| Wall-clock spent before the first edit vs after | Split of orientation cost against implementation cost |

Absence of friction is a result too. A phase with few calls, no retries and no
stalls is genuinely clean — record it and leave it alone.

---

## The downgrade rule

The purpose of the blind verifiers: decide whether a probe's struggle was caused
by the **repository** or by **that agent on that run**. Compare what the probe
spent against what a fresh, equally-capable agent spent on the same question.

| Verifier outcome | Verdict | Goes in report? |
| --- | --- | --- |
| `NOT_FOUND` | **CONFIRMED** — nobody can find it | Yes, at claimed severity |
| Found, `CONFIDENT: no` | **CONFIRMED** — discoverable but not trustworthy | Yes |
| Found in **≥ 6** calls | **CONFIRMED** — expensive for everyone | Yes |
| Found in **3–5** calls | **PARTIAL** — findable with effort | Yes, one severity lower |
| Found in **≤ 2** calls, `SOURCE` is a real file | **DOWNGRADED** — the answer was sitting there | No — drop it |

A `DOWNGRADED` finding means the probe was weak, not the repo. Dropping it is the
point; a report that keeps them trains you to distrust the whole document.

One exception: if the verifier's `SOURCE` is a file the probe demonstrably read
and *still* missed the answer, that is not agent weakness — it is a document that
buries its own conclusion. Keep it, reclassified as a documentation-clarity finding.

> **Tunable.** The `≤2` / `3–5` / `≥6` boundaries and the 10-call verifier ceiling
> are starting values, not measurements. Tighten them if the report fills with
> noise; loosen them if real gaps are getting dropped. Record the thresholds used
> in the report so two runs are comparable.

---

## Harness interference

Auto mode's classifier will block some things. Classification depends entirely on
**whether the blocked operation was necessary**, and getting this wrong either
launders a real defect into noise or blames the repo for a local setting.

**Repo finding (P0)** — the classifier blocked an operation genuinely required to
bootstrap, build, test, or run the project. Report as *"requires an operation an
autonomous agent should not be trusted to perform."* The fix is not to loosen
permissions; it is to remove the need — vendor the artefact, pin and checksum the
download, or wrap it in a reviewed script. Common instances: piping a remote
script to a shell, fetching an unpinned binary, `sudo`, writing outside the repo,
requiring credentials to run tests.

**Not a finding** — the probe *chose* a heavy-handed command when a safe
equivalent existed and was discoverable. That is the agent's judgement, not the
repo's fault. Note it in passing.

**Instrument noise** — denials, failures or limits caused by the local
environment rather than the repository: unrelated permission rules, no network,
missing personal credentials, sandbox restrictions. Quarantine these in their own
section. They never affect a phase verdict; they tell you the measurement was
partially blind, which is different from the repo being at fault.

---

## Guardrails

- **Never search the repo yourself to check a claim.** Filling the analyst's
  context with the answers destroys its ability to judge how discoverable those
  answers were. Dispatch a blind verifier instead.
- **No finding without evidence.** Every entry cites a journal line, a forensics
  number, a verifier verdict, or a diff deviation. Anything else is speculation.
- **Do not report the task's difficulty.** That the feature was intricate is not
  a readiness defect. Only report friction that documentation, tooling, or
  structure could have removed.
- **Report what worked.** A run that only lists problems reads as a demand to
  rewrite everything. Naming what was already effortless protects it from being
  "improved".
