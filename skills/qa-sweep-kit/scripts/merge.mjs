#!/usr/bin/env node
// Applies a reviewed dedupe plan to qa-sweep tickets: merges same-root-cause findings, retitles, records related pairs.
// Usage: node merge.mjs <tickets.json> <plan.json> <out.json>
// plan.json: { "merges": { "<keep-id>": ["<absorbed-id>", ...] }, "titles": { "<id>": "<new title>" }, "related_new": [["<id>", "<id>"], ...] }
// The kept ticket takes the highest severity of its group, the union of repos/related keys, and "both" platform when
// desktop and mobile reports merge; absorbed findings survive as also_observed (steps + evidence) for the filing script.
// Merges chain: { "A": ["B"], "B": ["C"] } keeps A and absorbs B and C. A cycle, or one id absorbed by two keeps, is an error.
import { readFileSync, writeFileSync } from "node:fs";

const [ticketsPath, planPath, outPath] = process.argv.slice(2);
const tickets = JSON.parse(readFileSync(ticketsPath, "utf8"));
const plan = JSON.parse(readFileSync(planPath, "utf8"));
const MERGES = plan.merges || {};
const TITLES = plan.titles || {};
const RELATED = plan.related_new || [];
const SEV = ["trivial", "minor", "major", "critical"];
const byId = Object.fromEntries(tickets.map((t) => [t.id, t]));
const keptBy = new Map();
for (const [keep, ids] of Object.entries(MERGES)) for (const id of ids) {
  if (keptBy.has(id) && keptBy.get(id) !== keep) throw new Error(`plan absorbs ${id} into both ${keptBy.get(id)} and ${keep}`);
  keptBy.set(id, keep);
}
for (const start of keptBy.keys()) {
  const chain = [start];
  for (let id = keptBy.get(start); id !== undefined; id = keptBy.get(id)) {
    const repeat = chain.includes(id);
    chain.push(id);
    if (repeat) throw new Error(`plan merges in a cycle: ${chain.join(" -> ")}`);
  }
}
const absorbed = new Set(keptBy.keys());
const groupOf = (id) => [...new Set(MERGES[id] || [])].flatMap((child) => [child, ...groupOf(child)]);
for (const id of [...Object.keys(MERGES), ...absorbed, ...Object.keys(TITLES), ...RELATED.flat()]) {
  if (!byId[id]) throw new Error(`plan names unknown finding id ${id}`);
}
const platformOf = (all) => {
  const p = new Set(all.map((x) => x.platform));
  if (p.size === 1) return [...p][0];
  const mobile = p.has("mobile") || p.has("both");
  const desktop = p.has("desktop") || p.has("both");
  return mobile && desktop ? "both" : all[0].platform;
};
const out = tickets.filter((t) => !absorbed.has(t.id)).map((t) => {
  const group = groupOf(t.id).map((id) => byId[id]);
  const all = [t, ...group];
  return {
    ...t,
    title: TITLES[t.id] || t.title,
    severity: SEV[Math.max(...all.map((x) => SEV.indexOf(x.severity)))],
    platform: platformOf(all),
    repos: [...new Set(all.flatMap((x) => x.repos || []))],
    related_existing: [...new Set(all.flatMap((x) => x.related_existing || []))],
    also_observed: [...(t.also_observed || []), ...group.flatMap((g) => [
      { id: g.id, area: g.area, title: g.title, actual: g.actual, steps: g.steps, evidence: g.evidence }, ...(g.also_observed || [])])],
    related_new: RELATED.filter((p) => p.includes(t.id)).map((p) => p.find((x) => x !== t.id)),
  };
});
writeFileSync(outPath, JSON.stringify(out, null, 1));
console.log(`in ${tickets.length}, absorbed ${absorbed.size}, out ${out.length}`);
