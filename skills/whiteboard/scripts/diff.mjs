#!/usr/bin/env node
// What changed on the board since the last look, and which @claude notes are open.
//
//   node diff.mjs <sceneId> [--keep]
//
// Compares the live scene with the snapshot saved by the previous run, then
// saves the live scene as the new snapshot (unless --keep). The first run on a
// scene has no snapshot: it reports open notes only.
import { getScene, cacheFile, readJson, writeJson, isMine } from "./cli.mjs";

const [sceneId, flag] = process.argv.slice(2);
if (!sceneId) {
  console.error("usage: node diff.mjs <sceneId> [--keep]");
  process.exit(1);
}

const live = getScene(sceneId);
const snapPath = cacheFile(sceneId, "snapshot.json");
const snap = readJson(snapPath, null);
const handled = readJson(cacheFile(sceneId, "handled.json"), {});
const byId = new Map(live.elements.map((e) => [e.id, e]));
const frameName = (e) => byId.get(e.frameId)?.name ?? null;

const brief = (e) => ({
  id: e.id, type: e.type, frame: frameName(e),
  text: e.text ?? byId.get(e.boundElements?.find((b) => b.type === "text")?.id)?.text,
  key: e.customData?.key, x: Math.round(e.x), y: Math.round(e.y), w: Math.round(e.width), h: Math.round(e.height),
});

const alive = live.elements.filter((e) => !e.isDeleted);
const bounds = alive.length ? {
  left: Math.round(Math.min(...alive.map((e) => e.x))), top: Math.round(Math.min(...alive.map((e) => e.y))),
  right: Math.round(Math.max(...alive.map((e) => e.x + e.width))), bottom: Math.round(Math.max(...alive.map((e) => e.y + e.height))),
} : null;
const frames = alive.filter((e) => e.type === "frame").map((e) => ({ id: e.id, name: e.name, key: e.customData?.key }));
const report = { sceneVersion: live.sceneVersion, bounds, frames, added: [], changed: [], deleted: [], openNotes: [] };
if (snap) {
  const old = new Map(snap.elements.map((e) => [e.id, e]));
  for (const e of live.elements) {
    const o = old.get(e.id);
    if (e.isDeleted) { if (o && !o.isDeleted) report.deleted.push(brief(o)); continue; }
    if (!o || o.isDeleted) report.added.push({ ...brief(e), by: isMine(e) ? "claude" : "user" });
    else if (o.version !== e.version) {
      const fields = Object.keys(e).filter((k) => !["version", "versionNonce", "updated"].includes(k) && JSON.stringify(e[k]) !== JSON.stringify(o[k]));
      report.changed.push({ ...brief(e), fields });
    }
  }
}
for (const e of live.elements) {
  if (e.isDeleted || e.type !== "text" || isMine(e)) continue;
  if ((e.text ?? "").toLowerCase().includes("@claude") && handled[e.id] !== e.version) {
    report.openNotes.push({ ...brief(e), version: e.version, containerId: e.containerId });
  }
}

console.log(JSON.stringify(report, null, 1));
if (flag !== "--keep") writeJson(snapPath, live);
