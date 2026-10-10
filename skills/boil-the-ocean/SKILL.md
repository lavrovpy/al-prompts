---
name: boil-the-ocean
description: Dig through every layer of a system for performance wins, extreme ones included, and come back with three distinct proposals.
disable-model-invocation: true
argument-hint: "[target]"
arguments: target
---

# Boil the ocean

Find every way to make `$target` faster, then bring back the three boldest proposals worth doing. Default `$target`: the performance problem under discussion in this session.

## Steps

1. **Baseline.** Measure the current cost with a repeatable command: latency, throughput, memory, bundle size, whichever the user cares about. Done when you have a number and the command that reproduces it.
2. **Profile.** Find where the cost goes. Done when most of the baseline is attributed to named hot spots, each backed by profiler output, a trace, or a timing.
3. **Sweep.** List every lever at every layer: algorithm and data structures, I/O and network, concurrency, caching and precomputation, memory and allocation, language and runtime, framework and dependencies, build and deploy, infrastructure and hardware, and the requirement itself (doing less work, or none). Rewrites, new languages, schema changes and cut features all count. Done when every layer has an entry or a line saying why it cannot help.
4. **Pick three.** Choose three proposals that differ in kind, each bolder than the safe fix the user would reach for unaided. Order them by ambition; the last should make the user flinch. For each give:
   - what changes, and which hot spot it hits
   - expected gain against the baseline, with the arithmetic or a quick spike behind it
   - cost: effort, what breaks, what it locks in
   - the first step to try it
5. **Leftovers.** After the three, list the remaining levers from the sweep, one line each.

Report and stop there: the user picks a proposal before anything is built.
