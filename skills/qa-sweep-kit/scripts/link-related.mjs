// Links related (but distinct) new tickets to each other with "Relates", using the filing ledger.
// Exits 1 when a pair could not be linked (HTTP error, or one ticket not in the ledger).
// Usage: JIRA_SITE=… JIRA_EMAIL=… JIRA_TOKEN_FILE=… node link-related.mjs <tickets.json> <ledger.json>  (tickets carry related_new: [ids])
import { readFileSync } from "node:fs";
const [ticketsPath, ledgerPath] = process.argv.slice(2);
const tickets = JSON.parse(readFileSync(ticketsPath, "utf8"));
const ledger = JSON.parse(readFileSync(ledgerPath, "utf8"));
const AUTH = "Basic " + Buffer.from(`${process.env.JIRA_EMAIL}:${readFileSync(process.env.JIRA_TOKEN_FILE, "utf8").trim()}`).toString("base64");
const pairs = new Set();
for (const t of tickets) for (const other of t.related_new || []) pairs.add([t.id, other].sort().join("|"));
const failed = [];
for (const p of pairs) {
  const [a, b] = p.split("|").map((id) => ledger[id]?.key);
  if (!a || !b) { failed.push(p); console.error(`${p}: not linked, a ticket is not filed`); continue; }
  const res = await fetch(`${process.env.JIRA_SITE}/rest/api/3/issueLink`, {
    method: "POST", headers: { Authorization: AUTH, "Content-Type": "application/json" },
    body: JSON.stringify({ type: { name: "Relates" }, inwardIssue: { key: a }, outwardIssue: { key: b } }),
  });
  if (res.ok) console.log(`${a} <-> ${b}: ${res.status}`);
  else { failed.push(p); console.error(`${a} <-> ${b}: HTTP ${res.status} ${(await res.text()).slice(0, 160)}`); }
}
console.log(`linked ${pairs.size - failed.length} of ${pairs.size}`);
if (failed.length) { console.error(`NOT LINKED: ${failed.join(", ")}`); process.exitCode = 1; }
