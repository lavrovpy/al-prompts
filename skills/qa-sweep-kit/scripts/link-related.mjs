#!/usr/bin/env node
// Links related (but distinct) new tickets to each other with "Relates", using the filing ledger.
// Each link goes into the ledger (the "linked" keys of the pair's first id, the same list file-jira.mjs keeps), so a
// rerun skips links already made. Exits 1 when a pair could not be linked (HTTP error, or one ticket not in the ledger).
// Usage: node link-related.mjs <tickets.json> <ledger.json>  (tickets carry related_new: [ids])
// Env: JIRA_SITE (https://x.atlassian.net), JIRA_EMAIL, JIRA_TOKEN_FILE (personal API token, basic auth).
import { readFileSync, writeFileSync } from "node:fs";
const [ticketsPath, ledgerPath] = process.argv.slice(2);
const need = (k) => process.env[k] || (() => { throw new Error(`set ${k}`); })();
const SITE = need("JIRA_SITE");
const AUTH = "Basic " + Buffer.from(`${need("JIRA_EMAIL")}:${readFileSync(need("JIRA_TOKEN_FILE"), "utf8").trim()}`).toString("base64");
const tickets = JSON.parse(readFileSync(ticketsPath, "utf8"));
const ledger = JSON.parse(readFileSync(ledgerPath, "utf8"));
const save = () => writeFileSync(ledgerPath, JSON.stringify(ledger, null, 2));
const pairs = new Set();
for (const t of tickets) for (const other of t.related_new || []) pairs.add([t.id, other].sort().join("|"));
const failed = [];
let skipped = 0;
for (const p of pairs) {
  const [idA, idB] = p.split("|");
  const [a, b] = [ledger[idA]?.key, ledger[idB]?.key];
  if (!a || !b) { failed.push(p); console.error(`${p}: not linked, a ticket is not filed`); continue; }
  if (ledger[idA].linked?.includes(b) || ledger[idB].linked?.includes(a)) { skipped++; continue; }
  const res = await fetch(`${SITE}/rest/api/3/issueLink`, {
    method: "POST", headers: { Authorization: AUTH, "Content-Type": "application/json" },
    body: JSON.stringify({ type: { name: "Relates" }, inwardIssue: { key: a }, outwardIssue: { key: b } }),
  });
  if (res.ok) { (ledger[idA].linked ??= []).push(b); save(); console.log(`${a} <-> ${b}: ${res.status}`); }
  else { failed.push(p); console.error(`${a} <-> ${b}: HTTP ${res.status} ${(await res.text()).slice(0, 160)}`); }
}
console.log(`linked ${pairs.size - failed.length - skipped} of ${pairs.size}, ${skipped} already linked`);
if (failed.length) { console.error(`NOT LINKED: ${failed.join(", ")}`); process.exitCode = 1; }
