#!/usr/bin/env node
// Files verified QA findings as Jira issues with attachments (ADF description, inline screenshots, mp4 videos).
// Usage: node file-jira.mjs <tickets.json> <ledger.json> [--limit N] [--only id1,id2] [--dry-run]
// Env: JIRA_SITE (https://x.atlassian.net), JIRA_EMAIL, JIRA_TOKEN_FILE (personal API token, basic auth),
//      JIRA_PROJECT (key), QA_LABEL (corpus label), QA_BUILD (e.g. "web origin/main abc1234"),
//      QA_PERSONAS (optional JSON file: {"user_name": "plain-words description"}), QA_CONVERTED_DIR (mp4 cache).
// The ledger records each finding's issue key, uploaded attachments and links, so a rerun picks up where the last one
// stopped without filing or uploading anything twice. Exits 1 when a ticket had no evidence file or a link failed.
import { readFileSync, writeFileSync, existsSync, statSync, mkdirSync, renameSync } from "node:fs";
import { basename, extname, join } from "node:path";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";

const [ticketsPath, ledgerPath, ...rest] = process.argv.slice(2);
const flag = (name) => { const i = rest.indexOf(name); return i === -1 ? undefined : rest[i + 1]; };
const LIMIT = Number(flag("--limit") ?? Infinity);
const ONLY = flag("--only")?.split(",");
const DRY = rest.includes("--dry-run");

const need = (k) => process.env[k] || (() => { throw new Error(`set ${k}`); })();
const SITE = need("JIRA_SITE");
const EMAIL = need("JIRA_EMAIL");
const PROJECT = need("JIRA_PROJECT");
const LABEL = need("QA_LABEL");
const TOKEN = readFileSync(process.env.JIRA_TOKEN_FILE, "utf8").trim();
const AUTH = "Basic " + Buffer.from(`${EMAIL}:${TOKEN}`).toString("base64");
const BUILD = need("QA_BUILD");
const CONVERTED = process.env.QA_CONVERTED_DIR || "/tmp/qa-sweep-converted";
mkdirSync(CONVERTED, { recursive: true });

const PRIORITY = { critical: "Highest", major: "High", minor: "Medium", trivial: "Low" };
const PERSONAS = process.env.QA_PERSONAS ? JSON.parse(readFileSync(process.env.QA_PERSONAS, "utf8")) : {};

// ---------- ADF helpers ----------
const text = (t, marks) => (marks ? { type: "text", text: t, marks } : { type: "text", text: t });
// Inline markdown subset: `code` and **bold**. Everything else is literal text.
function inline(s) {
  const out = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*)/g;
  let last = 0, m;
  const str = String(s ?? "");
  while ((m = re.exec(str))) {
    if (m.index > last) out.push(text(str.slice(last, m.index)));
    const tok = m[0];
    if (tok.startsWith("`")) out.push(text(tok.slice(1, -1), [{ type: "code" }]));
    else out.push(text(tok.slice(2, -2), [{ type: "strong" }]));
    last = m.index + tok.length;
  }
  if (last < str.length) out.push(text(str.slice(last)));
  return out.length ? out : [text(" ")];
}
const para = (s) => ({ type: "paragraph", content: inline(s) });
// Multi-line text -> paragraphs and fenced code blocks.
function blocks(s) {
  const str = String(s ?? "").trim();
  if (!str) return [];
  const out = [];
  const parts = str.split(/```(?:[a-z]*)\n?/);
  parts.forEach((part, i) => {
    if (i % 2 === 1) out.push({ type: "codeBlock", content: [{ type: "text", text: part.replace(/\n$/, "") || " " }] });
    else part.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean).forEach((p) => out.push(para(p.replace(/\n/g, " "))));
  });
  return out;
}
const heading = (t) => ({ type: "heading", attrs: { level: 3 }, content: [text(t)] });
const list = (items, ordered = false) => ({
  type: ordered ? "orderedList" : "bulletList",
  content: items.map((it) => ({ type: "listItem", content: [para(String(it).replace(/^\s*(\d+[.)]|[-*])\s+/, ""))] })),
});

function describe(t, mediaByPath) {
  const c = [];
  if (t.preconditions) c.push(heading("Preconditions"), ...blocks(t.preconditions));
  c.push(heading("Steps to reproduce"), list(t.steps, true));
  c.push(heading("Expected"), ...blocks(t.expected));
  c.push(heading("Actual"), ...blocks(t.actual));
  const ev = t.evidence || [];
  if (ev.length) {
    c.push(heading("Evidence"));
    c.push(list(ev.map((e) => `\`${uploadName(e.path)}\` — ${e.caption}`)));
    for (const e of ev) {
      const m = mediaByPath.get(e.path);
      if (m && isImage(e.path)) {
        c.push({ type: "mediaSingle", attrs: { layout: "center" }, content: [{ type: "media", attrs: { type: "file", id: m.fileId, collection: m.collection } }] });
      }
    }
  }
  if (t.acceptance_criteria?.length) c.push(heading("Acceptance criteria"), list(t.acceptance_criteria));
  if (t.developer_notes) c.push(heading("Notes"), ...blocks(t.developer_notes));
  for (const a of t.also_observed || []) {
    c.push(heading(`Same root cause, also seen: ${a.title}`), ...blocks(a.actual));
    if (a.steps?.length) c.push(list(a.steps, true));
  }
  const env = [
    `Build: ${BUILD}${t.repos?.length ? ` (${t.repos.join(", ")})` : ""}`,
    `Platform: ${t.platform}`,
    `Account: ${personaLine(t.persona)}`,
    `Reproducibility: ${t.reproducibility}`,
  ];
  if (t.environment_notes) env.push(`Note: ${t.environment_notes}`);
  c.push(heading("Environment"), list(env));
  return { type: "doc", version: 1, content: c };
}
function personaLine(p) {
  const s = String(p ?? "");
  const known = Object.keys(PERSONAS).filter((k) => s.includes(k));
  return known.length ? `${s} (${known.map((k) => `${k} = ${PERSONAS[k]}`).join("; ")})` : s;
}

// ---------- files ----------
const uploadName = (p) => (extname(p).toLowerCase() === ".webm" ? basename(p).replace(/\.webm$/i, ".mp4") : basename(p));
const isImage = (p) => /\.(png|jpe?g)$/i.test(p);
function prepare(p) {
  if (extname(p).toLowerCase() !== ".webm") return p;
  // Keyed by content, not name: every sweep reuses names like browse-01-…webm.
  const out = join(CONVERTED, createHash("sha256").update(readFileSync(p)).digest("hex").slice(0, 32) + ".mp4");
  if (!existsSync(out)) {
    const partial = `${out}.part.mp4`;
    execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-i", p, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-movflags", "+faststart", partial]);
    renameSync(partial, out);
  }
  return out;
}

// ---------- Jira REST ----------
async function jira(method, path, body, headers = {}) {
  const res = await fetch(`${SITE}${path}`, {
    method,
    headers: { Authorization: AUTH, Accept: "application/json", ...(body && !(body instanceof FormData) ? { "Content-Type": "application/json" } : {}), ...headers },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    redirect: "manual",
  });
  return res;
}
async function ok(res, what) {
  if (res.ok) return res.status === 204 ? null : res.json();
  throw new Error(`${what}: HTTP ${res.status} ${await res.text()}`);
}
async function attach(key, path, name) {
  const fd = new FormData();
  fd.append("file", new Blob([readFileSync(path)]), name);
  const [a] = await ok(await jira("POST", `/rest/api/3/issue/${key}/attachments`, fd, { "X-Atlassian-Token": "no-check" }), `attach ${name}`);
  return a;
}
// The attachment content URL redirects to the Media API; its file id lets the description embed the image inline.
async function mediaFileId(attachmentId) {
  const res = await jira("GET", `/rest/api/3/attachment/content/${attachmentId}?redirect=true`);
  const loc = res.headers.get("location") || "";
  const m = loc.match(/\/file\/([0-9a-f-]{36})\//);
  return m ? m[1] : null;
}

// ---------- main ----------
const tickets = JSON.parse(readFileSync(ticketsPath, "utf8"));
const ledger = existsSync(ledgerPath) ? JSON.parse(readFileSync(ledgerPath, "utf8")) : {};
const save = () => writeFileSync(ledgerPath, JSON.stringify(ledger, null, 2));
const usable = (e) => existsSync(e.path) && statSync(e.path).size > 0;
let filed = 0;
const skipped = [], incomplete = [];
for (const t of tickets) {
  if (ONLY && !ONLY.includes(t.id)) continue;
  if (ledger[t.id]?.done) continue;
  if (filed + incomplete.length >= LIMIT) break;
  const evidence = [...(t.evidence || []), ...(t.also_observed || []).flatMap((a) => a.evidence || [])];
  const present = evidence.filter(usable);
  const unusable = evidence.filter((e) => !usable(e)).map((e) => e.path);
  if (!present.length) { skipped.push(t.id); console.error(`SKIP ${t.id}: no evidence file exists (${unusable.join(", ")})`); continue; }
  if (unusable.length) console.error(`  ${t.id}: leaving out missing or empty evidence: ${unusable.join(", ")}`);
  t.evidence = (t.evidence || []).filter(usable);
  const labels = [
    LABEL,
    ...(t.repos || []).map((r) => `repo-${r}`),
    `area-${t.area}`,
    t.category,
    `severity-${t.severity}`,
    ...(t.platform === "mobile" || t.platform === "both" ? ["mobile"] : []),
  ].filter(Boolean);
  if (DRY) { console.log(JSON.stringify({ id: t.id, title: t.title, type: t.issue_type, labels, files: present.map((e) => uploadName(e.path)) })); filed++; continue; }

  const entry = (ledger[t.id] ??= { title: t.title });
  if (!entry.key) {
    const fields = { project: { key: PROJECT }, issuetype: { name: t.issue_type }, summary: t.title.slice(0, 254), labels };
    let res = await jira("POST", "/rest/api/3/issue", { fields: { ...fields, priority: { name: PRIORITY[t.severity] } } });
    if (res.status === 400) res = await jira("POST", "/rest/api/3/issue", { fields }); // priority not on this project's screen
    entry.key = (await ok(res, `create ${t.id}`)).key; save();
  }
  const key = entry.key;
  entry.attached ??= {};
  const mediaByPath = new Map();
  for (const e of present) {
    if (!entry.attached[e.path]) {
      const a = await attach(key, prepare(e.path), uploadName(e.path));
      const fileId = isImage(e.path) ? await mediaFileId(a.id).catch(() => null) : null;
      entry.attached[e.path] = { id: a.id, fileId }; save();
    }
    const { fileId } = entry.attached[e.path];
    if (fileId) mediaByPath.set(e.path, { fileId, collection: "" });
  }
  let res = await jira("PUT", `/rest/api/3/issue/${key}`, { fields: { description: describe(t, mediaByPath) } });
  if (!res.ok) {
    const err = await res.text();
    console.error(`  ${key}: inline images rejected (${res.status} ${err.slice(0, 160)}); retrying without them`);
    res = await jira("PUT", `/rest/api/3/issue/${key}`, { fields: { description: describe(t, new Map()) } });
  }
  await ok(res, `describe ${key}`);
  entry.linked ??= [];
  const failedLinks = [];
  for (const ext of new Set(t.related_existing || [])) {
    if (!new RegExp(`^${PROJECT}-\\d+$`).test(ext) || entry.linked.includes(ext)) continue;
    const r = await jira("POST", "/rest/api/3/issueLink", { type: { name: "Relates" }, inwardIssue: { key }, outwardIssue: { key: ext } });
    if (r.ok) { entry.linked.push(ext); save(); }
    else failedLinks.push(`${ext} (HTTP ${r.status} ${(await r.text()).slice(0, 160)})`);
  }
  if (failedLinks.length) {
    incomplete.push(t.id);
    console.error(`  ${key}: link failed: ${failedLinks.join("; ")}`);
    continue;
  }
  entry.done = true; save();
  filed++;
  console.log(`${key}\t${t.id}\t${t.issue_type}\t${t.severity}\t${t.title}`);
}
console.log(`filed ${filed}`);
if (skipped.length) console.error(`NOT FILED, no evidence file exists: ${skipped.join(", ")}`);
if (incomplete.length) console.error(`FILED WITHOUT ALL LINKS, rerun to retry: ${incomplete.join(", ")}`);
if (skipped.length || incomplete.length) process.exitCode = 1;
