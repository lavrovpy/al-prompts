// Board builder: frame-local drawing helpers that emit Excalidraw elements with
// stable IDs. Every element carries customData {owner: "claude", key}; the key
// is the element's identity across reruns, so give keys to anything you may
// change later (auto keys follow call order and shift when you insert calls).
import { createHash } from "node:crypto";

export const C = {
  fg: "#171613", fg2: "#3b3934", fg3: "#79756a",
  border: "#c9c4b8", borderStrong: "#a39e90",
  surface: "#f4f2ee", surface2: "#faf9f7", muted: "#e0ddd4",
  code: "#24231f", codeFg: "#f4f2ee",
  ember: "#ff5a1f", emberSoft: "#ffe3d0", emberText: "#c2330a",
};
export const SANS = 6; // Nunito: Excalidraw has no Geist
export const CODE = 3; // Cascadia

// Average glyph width per font size. Slightly above the real metrics
// (Nunito measures ~0.45) so boxes and frames never clip text.
const GLYPH = { [SANS]: 0.5, [CODE]: 0.6 };
const LINE = 1.25;
const ANCHOR = { l: [0, 0.5001], r: [1, 0.5001], t: [0.5001, 0], b: [0.5001, 1] };

const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";
// The API replaces IDs that don't look like Excalidraw's 21-char nanoids.
export function idFor(key) {
  const h = createHash("sha256").update(`whiteboard:${key}`).digest();
  return Array.from(h.subarray(0, 21), (b) => ALPHA[b & 63]).join("");
}

export function measure(str, size, font) {
  const lines = String(str).split("\n");
  return {
    w: Math.ceil(Math.max(...lines.map((l) => l.length)) * size * GLYPH[font]) + 4,
    h: Math.ceil(lines.length * size * LINE),
  };
}

function base(type, key, x, y, w, h, o = {}) {
  return {
    id: idFor(key), type, x, y, width: w, height: h, angle: 0,
    strokeColor: o.stroke ?? C.borderStrong, backgroundColor: o.fill ?? "transparent",
    fillStyle: "solid", strokeWidth: o.sw ?? 1, strokeStyle: o.dashed ? "dashed" : "solid",
    roughness: 0, opacity: 100, groupIds: [], frameId: null,
    roundness: o.round === false ? null : { type: 3 },
    // From hash bytes: parseInt on an idFor() string is NaN when it starts with "_" or "-".
    seed: createHash("sha256").update(`seed:${key}`).digest().readUInt32BE(0) % 2 ** 31,
    isDeleted: false, boundElements: [], link: null, locked: false,
    customData: { owner: "claude", key },
  };
}

// GitHub Light token colours.
export const SYNTAX = {
  plain: C.fg, comment: "#6e7781", string: "#0a3069", keyword: "#cf222e",
  constant: "#0550ae", entity: "#8250df",
};

const KEYWORDS = new Set((
  "and as assert async await break class continue def del elif else except finally for from global if " +
  "import in is lambda not or pass raise return try while with yield const let type typeof function export"
).split(" "));
const CONSTANTS = new Set(["None", "True", "False", "null", "true", "false", "undefined"]);

// Python, TypeScript and JSON, close enough for a board: one class per character.
function classify(line) {
  const cls = Array(line.length).fill("plain");
  const paint = (from, to, c) => { for (let i = from; i < to; i++) cls[i] = c; };
  let i = 0, prevWord = "";
  while (i < line.length) {
    const ch = line[i], rest = line.slice(i);
    if (ch === "#" || (rest.startsWith("//") && (i === 0 || line[i - 1] === " "))) {
      paint(i, line.length, "comment");
      break;
    }
    if (ch === '"' || ch === "'") {
      let j = i + 1;
      while (j < line.length && line[j] !== ch) j += line[j] === "\\" ? 2 : 1;
      paint(i, Math.min(j + 1, line.length), "string");
      i = j + 1;
      continue;
    }
    const word = /^@?[A-Za-z_][A-Za-z0-9_]*/.exec(rest)?.[0];
    if (word) {
      const call = line[i + word.length] === "(";
      const c = word.startsWith("@") ? "entity"
        : (word === "f" || word === "b") && /["']/.test(line[i + 1] ?? "") ? "string"
        : KEYWORDS.has(word) ? "keyword"
        : CONSTANTS.has(word) ? "constant"
        : prevWord === "def" || prevWord === "class" || call ? "entity" : "plain";
      paint(i, i + word.length, c);
      prevWord = word;
      i += word.length;
      continue;
    }
    const num = /^\d[\d_.]*/.exec(rest)?.[0];
    if (num && !/[A-Za-z_]/.test(line[i - 1] ?? "")) {
      paint(i, i + num.length, "constant");
      i += num.length;
      continue;
    }
    i++;
  }
  return cls;
}

// One string per colour, other characters blanked to spaces. In a monospace font
// the layers line up exactly, whatever the renderer's glyph width.
export function highlightLayers(src) {
  const layers = {};
  const lines = src.split("\n");
  lines.forEach((line, n) => {
    classify(line).forEach((c, i) => {
      layers[c] ??= lines.map(() => []);
      layers[c][n][i] = line[i];
    });
  });
  layers.plain ??= lines.map(() => []);
  return Object.fromEntries(Object.entries(layers).map(([c, ls]) => [
    c, ls.map((chars, n) => Array.from({ length: lines[n].length }, (_, i) => chars[i] ?? " ").join("").trimEnd()).join("\n"),
  ]));
}

export class Board {
  constructor() {
    this.frames = [];
  }

  frame(key, name) {
    const f = new Frame(key, name);
    this.frames.push(f);
    return f;
  }

  // columns: arrays of frame keys, laid out left to right, stacked top to bottom,
  // starting at origin {x, y}. On a scene that already has content, start right
  // of the bounds diff.mjs reports, so new frames never land on existing ones.
  layout(columns, { gap = 160, x: x0 = 0, y: y0 = 0 } = {}) {
    const byKey = new Map(this.frames.map((f) => [f.key, f]));
    let x = x0;
    for (const col of columns) {
      let y = y0, colW = 0;
      for (const k of col) {
        const f = byKey.get(k);
        f.fit();
        f.place(x, y);
        y += f.el.height + gap;
        colW = Math.max(colW, f.el.width);
      }
      x += colW + gap;
    }
    return this;
  }

  // Children first, then their frame: Excalidraw expects a frame after its children.
  elements() {
    return this.frames.flatMap((f) => [...f.els, f.el]);
  }
}

class Frame {
  constructor(key, name) {
    this.key = key;
    this.n = 0;
    this.els = [];
    this.el = { ...base("frame", key, 0, 0, 100, 100, { stroke: C.fg3, round: false }), name };
  }

  k(key, kind) {
    return `${this.key}/${key ?? `${kind}${++this.n}`}`;
  }

  push(e) {
    e.frameId = this.el.id;
    this.els.push(e);
    return e;
  }

  text(x, y, str, o = {}) {
    const size = o.size ?? 20, font = o.font ?? SANS;
    const m = measure(str, size, font);
    const t = base("text", o.k ?? this.k(o.key, "text"), x, y, o.w ?? m.w, m.h, { ...o, round: false });
    Object.assign(t, {
      strokeColor: o.color ?? C.fg, text: str, originalText: str, fontSize: size, fontFamily: font,
      textAlign: o.align ?? "left", verticalAlign: o.valign ?? "top",
      containerId: o.containerId ?? null, autoResize: true, lineHeight: LINE,
    });
    return this.push(t);
  }

  rect(x, y, w, h, o = {}) {
    return this.push(base("rectangle", this.k(o.key, "rect"), x, y, w, h, o));
  }

  // Rectangle with a bound label, centred or left-aligned with 20 px padding.
  box(x, y, w, h, label, o = {}) {
    const r = this.rect(x, y, w, h, { fill: C.surface, stroke: C.borderStrong, ...o });
    const size = o.size ?? 20, font = o.font ?? SANS, align = o.align ?? "center";
    const m = measure(label, size, font);
    const t = this.text(align === "center" ? x + (w - m.w) / 2 : x + 20, y + (h - m.h) / 2, label, {
      size, font, color: o.color ?? C.fg, align, valign: "middle", containerId: r.id,
      w: align === "center" ? m.w : w - 40, k: `${r.customData.key}:label`,
    });
    r.boundElements.push({ id: t.id, type: "text" });
    return r;
  }

  // Straight arrow between box edges ("l", "r", "t", "b"), bound at both ends.
  arrow(from, fs, to, ts, label = "", o = {}) {
    const edge = (r, s) => ({
      l: [r.x, r.y + r.height / 2], r: [r.x + r.width, r.y + r.height / 2],
      t: [r.x + r.width / 2, r.y], b: [r.x + r.width / 2, r.y + r.height],
    })[s];
    const [x1, y1] = edge(from, fs), [x2, y2] = edge(to, ts);
    const gap = 6, len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const ux = (x2 - x1) / len, uy = (y2 - y1) / len;
    const sx = x1 + ux * gap, sy = y1 + uy * gap, ex = x2 - ux * gap, ey = y2 - uy * gap;
    const a = base("arrow", this.k(o.key, "arrow"), sx, sy, Math.abs(ex - sx), Math.abs(ey - sy), {
      ...o, stroke: o.stroke ?? C.fg2, sw: 2, round: false,
    });
    Object.assign(a, {
      roundness: { type: 2 }, points: [[0, 0], [ex - sx, ey - sy]],
      // The API accepts only this binding form; the older {focus, gap} is rejected.
      // fixedPoint is the anchor as a fraction of the box; 0.5001 is what the editor writes.
      startBinding: { elementId: from.id, fixedPoint: ANCHOR[fs], mode: "orbit" },
      endBinding: { elementId: to.id, fixedPoint: ANCHOR[ts], mode: "orbit" },
      startArrowhead: null, endArrowhead: "arrow", elbowed: false,
    });
    this.push(a);
    from.boundElements.push({ id: a.id, type: "arrow" });
    to.boundElements.push({ id: a.id, type: "arrow" });
    if (label) {
      const m = measure(label, 16, SANS);
      const t = this.text((sx + ex) / 2 - m.w / 2, (sy + ey) / 2 - m.h / 2, label, {
        size: 16, color: C.fg3, align: "center", valign: "middle", containerId: a.id, k: `${a.customData.key}:label`,
      });
      a.boundElements.push({ id: t.id, type: "text" });
    }
    return a;
  }

  // Dashed outline with an uppercase eyebrow: where the boxes inside run.
  group(x, y, w, h, eyebrow, o = {}) {
    const r = this.rect(x, y, w, h, { dashed: true, stroke: C.borderStrong, key: o.key });
    this.text(x + 16, y + 12, eyebrow, { size: 14, color: C.fg3, key: o.key && `${o.key}:eyebrow` });
    return r;
  }

  // Light code panel with syntax colours, optional caption above it. Returns the panel's size.
  // Excalidraw colours a whole text element, so each colour is its own layer
  // (see highlightLayers); panel and layers share a group and move together.
  code(x, y, src, o = {}) {
    const size = o.size ?? 16, m = measure(src, size, CODE);
    const w = Math.max(o.minW ?? 0, m.w + 48), h = m.h + 40, key = this.k(o.key, "code");
    if (o.caption) this.text(x, y - 30, o.caption, { size: 16, color: C.fg3, k: `${key}:caption` });
    const group = [idFor(`${key}:group`)];
    const panel = this.push(base("rectangle", `${key}:panel`, x, y, w, h, { fill: C.surface2, stroke: C.border }));
    panel.groupIds = group;
    for (const [cls, text] of Object.entries(highlightLayers(src))) {
      const t = this.text(x + 24, y + 20, text, {
        size, font: CODE, color: SYNTAX[cls], k: cls === "plain" ? `${key}:src` : `${key}:src:${cls}`,
      });
      t.groupIds = group;
    }
    return { w, h };
  }

  // Eyebrow, title and the short ember rule under it.
  heading(eyebrow, title, o = {}) {
    const x = o.x ?? 60, y = o.y ?? 50;
    this.text(x, y, eyebrow, { size: 16, color: C.emberText, key: "heading:eyebrow" });
    this.text(x, y + 28, title, { size: 40, key: "heading:title" });
    this.push(base("rectangle", this.k("heading:rule"), x, y + 86, 64, 4, { fill: C.ember, stroke: C.ember, round: false }));
  }

  fit(pad = 60) {
    const free = this.els.filter((e) => !e.containerId);
    this.el.width = Math.max(...free.map((e) => e.x + e.width)) + pad;
    this.el.height = Math.max(...free.map((e) => e.y + e.height)) + pad;
  }

  place(x, y) {
    this.el.x = x;
    this.el.y = y;
    for (const e of this.els) { e.x += x; e.y += y; }
  }
}
