#!/usr/bin/env node
// Estimates API-list-price cost of Claude Code transcripts.
// Usage: node cost.mjs <label>=<file-or-dir> [...]   (dirs: every agent-*.jsonl inside, grouped by .meta.json description)
// Usage lines are deduplicated by message id: Claude Code logs one line per content block with identical usage.
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";

// $ per million tokens. Haiku 5.5 bills prompts over 100K tokens at 5x ("@long"); its cache read is assumed at 0.1x of input.
const PRICES = {
  "claude-opus-5-5": { in: 4, out: 20, w5: 5, w1h: 8, read: 0.2 },
  "claude-sonnet-5-5": { in: 2, out: 10, w5: 2.5, w1h: 4, read: 0.2 },
  "claude-haiku-5-5": { in: 0.1, out: 0.5, w5: 0.125, w1h: 0.2, read: 0.01 },
  "claude-haiku-5-5@long": { in: 0.5, out: 2.5, w5: 0.625, w1h: 1.0, read: 0.05 },
};

function usageOf(file) {
  const byId = new Map();
  for (const line of readFileSync(file, "utf8").split("\n")) {
    if (!line.includes('"usage"')) continue;
    let rec; try { rec = JSON.parse(line); } catch { continue; }
    const m = rec.message;
    if (!m?.usage || !m.id || rec.type !== "assistant") continue;
    const prev = byId.get(m.id);
    if (!prev || (m.usage.output_tokens ?? 0) >= (prev.usage.output_tokens ?? 0)) byId.set(m.id, { model: m.model, usage: m.usage });
  }
  return [...byId.values()];
}
const LONG_PROMPT = { "claude-haiku-5-5": 100_000 };
function add(acc, { model, usage: u }) {
  const prompt = (u.input_tokens ?? 0) + (u.cache_read_input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0);
  if (LONG_PROMPT[model] && prompt > LONG_PROMPT[model]) model = `${model}@long`;
  const a = (acc[model] ??= { calls: 0, in: 0, out: 0, w5: 0, w1h: 0, read: 0 });
  a.calls++; a.in += u.input_tokens ?? 0; a.out += u.output_tokens ?? 0; a.read += u.cache_read_input_tokens ?? 0;
  const cc = u.cache_creation ?? {};
  const w1h = cc.ephemeral_1h_input_tokens ?? 0;
  a.w1h += w1h; a.w5 += cc.ephemeral_5m_input_tokens ?? Math.max(0, (u.cache_creation_input_tokens ?? 0) - w1h);
}
function dollars(acc) {
  let total = 0; const per = {};
  for (const [model, a] of Object.entries(acc)) {
    const p = PRICES[model]; if (!p) { per[model] = { ...a, usd: null }; continue; }
    const usd = (a.in * p.in + a.out * p.out + a.w5 * p.w5 + a.w1h * p.w1h + a.read * p.read) / 1e6;
    per[model] = { ...a, usd: +usd.toFixed(2), parts: { input: +(a.in * p.in / 1e6).toFixed(2), output: +(a.out * p.out / 1e6).toFixed(2), cacheWrite: +((a.w5 * p.w5 + a.w1h * p.w1h) / 1e6).toFixed(2), cacheRead: +(a.read * p.read / 1e6).toFixed(2) } };
    total += usd;
  }
  return { total: +total.toFixed(2), per };
}

const report = {};
for (const arg of process.argv.slice(2)) {
  const [label, path] = arg.split("=");
  if (statSync(path).isDirectory()) {
    const groups = {};
    for (const f of readdirSync(path).filter((f) => /^agent-.*\.jsonl$/.test(f))) {
      const metaPath = join(path, f.replace(/\.jsonl$/, ".meta.json"));
      const desc = existsSync(metaPath) ? JSON.parse(readFileSync(metaPath, "utf8")).description : f;
      const acc = {}; usageOf(join(path, f)).forEach((u) => add(acc, u));
      groups[desc] = dollars(acc);
    }
    const all = {}; for (const f of readdirSync(path).filter((f) => /^agent-.*\.jsonl$/.test(f))) usageOf(join(path, f)).forEach((u) => add(all, u));
    report[label] = { ...dollars(all), agents: groups };
  } else {
    const acc = {}; usageOf(path).forEach((u) => add(acc, u)); report[label] = dollars(acc);
  }
}
console.log(JSON.stringify(report, null, 1));
