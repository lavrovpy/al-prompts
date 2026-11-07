// Shared helpers for the scripts: the pinned CLI, per-scene cache files, and
// fractional index keys for new elements.
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

// Pinned: the scene-content behaviour in SKILL.md was verified on this version.
const CLI = ["-y", "@excalidraw/cli@0.3.0"];

export function excalidraw(args, { input } = {}) {
  return execFileSync("npx", [...CLI, ...args], {
    input, encoding: "utf8", maxBuffer: 256 * 1024 * 1024, stdio: ["pipe", "pipe", "pipe"],
  });
}

export const getScene = (sceneId) => JSON.parse(excalidraw(["scenes", "content", "get", sceneId]));

export function patchScene(sceneId, payload) {
  return excalidraw(["scenes", "content", "patch", sceneId, "--file", "-"], { input: JSON.stringify(payload) });
}

export function cacheFile(sceneId, name) {
  const dir = join(process.env.XDG_CACHE_HOME ?? join(homedir(), ".cache"), "whiteboard", sceneId);
  mkdirSync(dir, { recursive: true });
  return join(dir, name);
}

export const readJson = (path, fallback) => (existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : fallback);
export const writeJson = (path, data) => writeFileSync(path, JSON.stringify(data));

export const isMine = (e) => e?.customData?.owner === "claude";

// New keys sort after every existing index: the current top key plus a
// fixed-width suffix. The alphabet omits "0" because a fractional key may not
// end in zero, and it is in ASCII order, so the suffixes sort as numbers do.
const DIGITS = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
export function indexAllocator(elements) {
  const top = elements.reduce((m, e) => (e.index && e.index > m ? e.index : m), "a0");
  let n = 0;
  return () => {
    let i = n++, s = "";
    for (let d = 0; d < 3; d++) { s = DIGITS[i % DIGITS.length] + s; i = Math.floor(i / DIGITS.length); }
    return top + s;
  };
}

export const nonce = () => Math.floor(Math.random() * 2 ** 31);
