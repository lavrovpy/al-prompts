#!/usr/bin/env node
// Write a generated board into a live scene without overwriting the user's edits.
//
//   node sync.mjs <sceneId> <board.mjs> [--at x,y] [--dry <outDir>]
//
// <board.mjs> default-exports (Board, {x, y}) => Board; --at sets that origin.
// The merge is three-way per
// field: live (the scene now), written (what this script last stored, cached
// per scene), generated (the board module). A field the user changed since the
// last write keeps the user's value; every other field takes the generated one.
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { mkdirSync, writeFileSync } from "node:fs";
import { Board } from "../lib/board.mjs";
import { getScene, patchScene, cacheFile, readJson, writeJson, isMine, indexAllocator, nonce, excalidraw } from "./cli.mjs";

const [sceneId, modPath, ...rest] = process.argv.slice(2);
const opt = (name) => { const i = rest.indexOf(name); return i < 0 ? undefined : rest[i + 1] ?? ""; };
if (!sceneId || !modPath) {
  console.error("usage: node sync.mjs <sceneId> <board.mjs> [--at x,y] [--dry <outDir>]");
  process.exit(1);
}
const outDir = opt("--dry"), dry = outDir !== undefined;
const [atX = 0, atY = 0] = (opt("--at") ?? "0,0").split(",").map(Number);

const build = (await import(pathToFileURL(resolve(modPath)).href)).default;
const generated = build(new Board(), { x: atX, y: atY }).elements();

const live = getScene(sceneId);
const liveById = new Map(live.elements.map((e) => [e.id, e]));
const writtenPath = cacheFile(sceneId, "written.json");
const written = readJson(writtenPath, {});
const nextIndex = indexAllocator(live.elements);

const META = new Set(["version", "versionNonce", "updated", "index", "seed", "boundElements"]);
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const content = (e) => Object.fromEntries(Object.entries(e).filter(([k]) => !META.has(k)));
const bump = (e) => ({ ...e, version: (e.version ?? 0) + 1, versionNonce: nonce(), updated: Date.now() });
const genIds = new Set(generated.map((g) => g.id));

const out = [], summary = { added: 0, updated: 0, keptUserEdits: 0, skippedUserDeleted: 0, removed: 0 };

for (const g of generated) {
  const l = liveById.get(g.id), w = written[g.id];
  if (!l) {
    out.push({ ...g, index: nextIndex(), version: 1, versionNonce: nonce(), updated: Date.now() });
    summary.added++;
    continue;
  }
  if (l.isDeleted) {
    // Still in the written cache: the user deleted it, so it stays deleted.
    // Not in the cache: an earlier sync removed it, so the board may bring it back.
    if (w) { summary.skippedUserDeleted++; continue; }
    out.push({ ...g, index: l.index, version: l.version + 1, versionNonce: nonce(), updated: Date.now() });
    summary.added++;
    continue;
  }
  const merged = { ...l };
  let kept = false;
  for (const k of Object.keys(g)) {
    if (META.has(k)) continue;
    const userChanged = w ? !same(l[k], w[k]) : !isMine(l);
    if (userChanged) kept ||= !same(l[k], g[k]);
    else merged[k] = g[k];
  }
  // Bindings: keep arrows the user attached and add the generated ones.
  const ids = new Set();
  merged.boundElements = [...(l.boundElements ?? []), ...(g.boundElements ?? [])]
    .filter((b) => !ids.has(b.id) && ids.add(b.id));
  if (kept) summary.keptUserEdits++;
  if (same(content(merged), content(l)) && same(merged.boundElements, l.boundElements ?? [])) continue;
  out.push(bump(merged));
  summary.updated++;
}

// Elements this script wrote before that the board no longer generates.
for (const [id, w] of Object.entries(written)) {
  const l = liveById.get(id);
  if (genIds.has(id) || !l || l.isDeleted || !isMine(l)) continue;
  if (!same(content(l), content(w))) continue; // the user edited it since: keep it
  out.push(bump({ ...l, isDeleted: true }));
  summary.removed++;
}

console.log(JSON.stringify({ sceneId, dry, ...summary, patchSize: out.length }));

if (dry) {
  const dir = resolve(outDir ?? "whiteboard-preview");
  mkdirSync(dir, { recursive: true });
  const byId = new Map(live.elements.map((e) => [e.id, e]));
  for (const e of out) byId.set(e.id, e);
  const preview = { type: "excalidraw", version: 2, elements: [...byId.values()], appState: live.appState, files: live.files ?? {} };
  writeFileSync(`${dir}/patch.json`, JSON.stringify({ elements: out }));
  writeFileSync(`${dir}/preview.excalidraw`, JSON.stringify(preview));
  console.log(excalidraw(["render", `${dir}/preview.excalidraw`, "--all-frames", "--out", `${dir}/frames/`]));
  process.exit(0);
}

if (out.length) patchScene(sceneId, { elements: out });
// The stored scene becomes the base for the next three-way merge.
const after = getScene(sceneId);
for (const e of after.elements) if (genIds.has(e.id) && !e.isDeleted) written[e.id] = e;
for (const id of Object.keys(written)) if (!genIds.has(id)) delete written[id];
writeJson(writtenPath, written);
