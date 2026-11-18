---
name: deepen
description: Rewrite a task as a deeper version of itself, not a bigger one: the expert's moves, the rawest inputs, real methods, and an outside judge.
disable-model-invocation: true
argument-hint: "[task or prompt]"
arguments: task
---

# Deepen

Rewrite `$task` so it asks for the work a top professional in the field would do, at the same scope. Default `$task`: the request most recently made in this session.

**Deeper, not bigger.** The deeper version answers the same question for the same goal, with rawer inputs, stronger methods and outside proof. It keeps the deliverable as it is. An idea that changes what gets delivered goes in the report's *Bigger* list, not in the rewrite.

Before step 1, state in one line the outcome the task serves. If the request and the session don't show it, ask once. Judge every answer below against that outcome.

## Steps

1. **The professional.** Name the specific role whose daily job is this problem (a site reliability engineer, a survival analyst, a forensic accountant), then list what they would do here that the task doesn't ask for. Write each item as an action they take, the way they actually work. Done when every item is an action you could watch someone perform, with no qualities like "rigorous" standing in for one.
2. **Raw material.** For each input the task uses or implies, name the upstream source it was digested from: the dashboard comes from the event table, the summary from the transcripts, the bug report from the crash dump and the commit that shipped it. Look for each source in the environment (repo, databases, logs, connectors, files on disk) and mark it *reachable* (with the path, query or tool that reaches it), *needs access* (what the user must grant), or *missing*. Done when every input has an upstream source and a mark backed by an actual lookup.
3. **Methods and tools.** Name the methods the professional would apply and the tools they would run: bisection, survival analysis, differential diagnosis, a flame graph, a held-out set; DuckDB, `perf`, `git bisect`, a notebook. For each, say what it produces that the current approach cannot. A method that changes only the vocabulary of the answer is a *costume*; drop it. Done when every method has a distinct output and every tool is one you could install or call here.
4. **Outside judge.** Name what, other than you or the user, will show the result is right: a test that goes red then green, a reproduction from raw data, a prediction scored on held-out data, a benchmark, a compiler, a reviewer with a stake in the outcome, a measurement taken next week. Prefer a judge you can run now. If none exists, building one becomes part of the rewritten task. Done when the judge is named with a pass condition stated as a concrete value.
5. **Rewrite.** Write the deeper prompt, self-contained so a fresh agent with no access to this session could run it. It states the goal, the raw sources and how to reach them, the methods, the outside judge and its pass condition, and a target harder than the user would set unaided. Done when every surviving item from steps 1–4 appears in it, and it still asks the original question for the original deliverable.

## Report

- The goal line.
- Steps 1–4, a few lines each.
- The rewritten prompt in one fenced block, ready to copy.
- **Needs from you**: each *needs access* source, if any.
- **Bigger**: ideas that would change the deliverable, one line each, if any.

Then stop. The user runs the prompt, edits it, or tells you to run it.
