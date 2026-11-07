#!/usr/bin/env node
// Answer a note: an ember sticky note to the right of it, text prefixed
// "claude:", then the note is marked handled so the watcher skips it.
//
//   node reply.mjs <sceneId> <noteTextId> <reply text | -> [--dry]
//
// Rerunning for the same note updates the same reply. "-" reads the text from stdin.
import { readFileSync } from "node:fs";
import { idFor, C, SANS } from "../lib/board.mjs";
import { getScene, patchScene, cacheFile, readJson, writeJson, indexAllocator, nonce } from "./cli.mjs";

const [sceneId, noteId, raw, flag] = process.argv.slice(2);
if (!sceneId || !noteId || !raw) {
  console.error("usage: node reply.mjs <sceneId> <noteTextId> <reply text | -> [--dry]");
  process.exit(1);
}

const live = getScene(sceneId);
const byId = new Map(live.elements.map((e) => [e.id, e]));
const note = byId.get(noteId);
if (!note || note.type !== "text") throw new Error(`no text element ${noteId} in scene ${sceneId}`);
const anchor = byId.get(note.containerId) ?? note;

const COLS = 38, SIZE = 20, LH = 1.25;
const wrap = (s) => s.split("\n").flatMap((para) => {
  const lines = [];
  let cur = "";
  for (const word of para.split(/\s+/).filter(Boolean)) {
    if (cur && (cur + " " + word).length > COLS) { lines.push(cur); cur = word; }
    else cur = cur ? `${cur} ${word}` : word;
  }
  return [...lines, cur];
}).join("\n");

const body = (raw === "-" ? readFileSync(0, "utf8") : raw).trim();
const text = wrap(body.startsWith("claude:") ? body : `claude: ${body}`);
const lines = text.split("\n").length;
const W = 440, H = Math.round(lines * SIZE * LH + 70);

const key = `reply:${anchor.id}`;
// Find an earlier reply by its key, so replies made with other ID schemes are reused.
const byKey = (type) => live.elements.find((e) => !e.isDeleted && e.type === type && e.customData?.key === key);
const prev = { s: byKey("stickynote"), t: byKey("text") };
const sid = prev.s?.id ?? idFor(`${key}:note`), tid = prev.t?.id ?? idFor(`${key}:text`);
const own = { owner: "claude", key, replyTo: noteId };
const next = indexAllocator(live.elements);
const stamp = (old) => ({
  version: (old?.version ?? 0) + 1, versionNonce: nonce(), updated: Date.now(),
  index: old?.index ?? next(), seed: old?.seed ?? nonce(), isDeleted: false,
});

// Keep the reply where the user moved it, if they did.
const x = prev.s?.x ?? anchor.x + anchor.width + 40, y = prev.s?.y ?? anchor.y;
const sticky = {
  id: sid, type: "stickynote", x, y, width: W, height: H, baseHeight: H, angle: 0,
  strokeColor: C.emberText, backgroundColor: C.emberSoft, fillStyle: "solid", strokeWidth: 2,
  strokeStyle: "solid", roughness: 1, opacity: 100, groupIds: [], frameId: anchor.frameId ?? null,
  roundness: { type: 2 }, boundElements: [{ type: "text", id: tid }], link: null, locked: false,
  customData: own, ...stamp(prev.s),
};
const label = {
  id: tid, type: "text", x: x + 20, y: y + 35, width: W - 40, height: lines * SIZE * LH, angle: 0,
  strokeColor: C.code, backgroundColor: "transparent", fillStyle: "solid", strokeWidth: 1,
  strokeStyle: "solid", roughness: 0, opacity: 100, groupIds: [], frameId: anchor.frameId ?? null,
  roundness: null, boundElements: null, link: null, locked: false, text, originalText: body,
  fontSize: SIZE, fontFamily: SANS, textAlign: "left", verticalAlign: "middle",
  containerId: sid, autoResize: true, lineHeight: LH, customData: own, ...stamp(prev.t),
};

if (flag === "--dry") {
  console.log(JSON.stringify({ elements: [sticky, label] }, null, 1));
  process.exit(0);
}
patchScene(sceneId, { elements: [sticky, label] });
const handledPath = cacheFile(sceneId, "handled.json");
writeJson(handledPath, { ...readJson(handledPath, {}), [noteId]: note.version });
console.log(JSON.stringify({ replied: noteId, noteVersion: note.version, stickyId: sid }));
