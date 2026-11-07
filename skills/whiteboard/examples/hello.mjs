// Minimal board: one frame, a three-step flow inside a group, a code panel.
// Coordinates are local to the frame; layout() places the frames.
// Leave at least the label's width plus 60 px between boxes joined by a labelled arrow.
import { C } from "../lib/board.mjs";

export default function build(b, { x = 0, y = 0 } = {}) {
  const f = b.frame("hello", "01 · hello");
  f.heading("01 · EXAMPLE", "A request, its handler, and the store");
  f.group(40, 190, 1360, 300, "YOUR MAC", { key: "mac" });
  const a = f.box(80, 260, 300, 160, "client\n\nsends JSON", { key: "client" });
  const h = f.box(560, 260, 300, 160, "handler()\n\nvalidates", { key: "handler" });
  const s = f.box(1040, 260, 320, 160, "store\n\nthe one box this\nanswer is about", {
    key: "store", fill: C.emberSoft, stroke: C.ember, color: C.emberText, sw: 2,
  });
  f.arrow(a, "r", h, "l", "POST /items", { key: "a1" });
  f.arrow(h, "r", s, "l", "Item", { key: "a2" });
  f.code(60, 580, `class Item(BaseModel):\n    name: str\n    qty: int = 1`, { key: "model", caption: "the contract" });
  return b.layout([["hello"]], { x, y });
}
