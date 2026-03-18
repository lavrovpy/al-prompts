---
name: text-to-svg-for-slide
description: >
  This skill should be used when the user asks to "create an SVG slide",
  "generate an SVG diagram", "make an SVG infographic", "convert text to SVG",
  "build a visual slide in SVG", "design an SVG presentation", "SVG for a deck",
  "fix SVG rendering", or wants any standalone SVG intended for embedding in
  tools like Miro, Figma, Notion, Google Slides, or email. It is also relevant
  when the user needs to fix an existing SVG that renders with black boxes,
  missing colors, or invisible text due to missing embedded styles or CSS
  custom properties.
version: 0.1.0
---

# Text-to-SVG for Slides

Generate self-contained, portable SVG files for slides and diagrams that render
correctly in any environment — browsers, Miro, Figma, Notion, email clients,
and other tools that strip or ignore external stylesheets.

## Critical Rule: Self-Contained SVGs

Every SVG produced by this skill MUST be fully self-contained. External
renderers have no access to external CSS, CSS custom properties, or modern
SVG features. Violating this rule causes black boxes, missing colors, and
invisible text.

### Mandatory Checklist

Before finishing any SVG, verify all of the following:

1. **Embedded `<style>` block** — Define all CSS classes inside the SVG's
   `<style>` element. Never rely on an external stylesheet.
2. **No `var(--x)` references** — Replace every CSS custom property with an
   explicit color value (e.g., `var(--b)` → `#16213E`).
3. **No `context-stroke` or `context-fill`** — These are modern CSS properties
   unsupported in most SVG renderers. Create separate `<marker>` definitions
   with hardcoded colors for each stroke color needed.
4. **Explicit `fill` on standalone text** — Text elements outside a styled `<g>`
   must have an explicit `fill` attribute (default SVG fill is black).
5. **Add `xmlns="http://www.w3.org/2000/svg"`** — Required for SVGs used
   outside HTML documents.

## Equal Padding in Content Boxes

Uneven padding is the most common SVG slide mistake. Text that crowds the
bottom or side of a box looks broken. Follow this padding-first algorithm
for EVERY box that contains text.

Always use `dominant-baseline="central"` on all text elements. With this
setting, the `y` coordinate IS the vertical center of the text glyph.

### The Algorithm (mandatory for all content boxes)

**Step 1 — Choose a uniform padding P.**
Use 6–8px for small boxes (height < 60px), 10–12px for larger ones.
This padding applies equally to top, bottom, left, and right.

**Step 2 — Center all text lines as a group at the box center.**
For N lines with inter-line gap G (typically 11–12px):

```
box_center = height / 2
total_span = (N - 1) * G
first_y    = box_center - total_span / 2
line_i_y   = first_y + i * G        (i = 0, 1, …, N-1)
```

For horizontal positioning:
- Centered text: `text_x = width / 2` with `text-anchor="middle"`
- Left-aligned text: `text_x = P` (or P + bullet offset for lists)

**Step 3 — Verify padding is respected on all four sides.**
After computing positions, CHECK that no text glyph extends into the
padding zone:

```
top_clearance    = first_y - (largest_font_size / 2)
bottom_clearance = height - (last_y + largest_font_size / 2)
left_clearance   = text_x for left-aligned text
right_clearance  = width - text_x for left-aligned (estimate text width),
                   or width/2 - estimated_half_text_width for centered
```

ALL clearances MUST be >= P. If any clearance is less than P, increase the
box dimensions — never shrink the padding.

### Worked Example

Box: width=200, height=58. Four lines: 9px bold title + three 7.5px body lines.
Choose P = 6, G = 11.

```
box_center = 58 / 2 = 29
total_span = 3 * 11 = 33
first_y    = 29 - 33/2 = 29 - 16.5 = 12.5  → round to 12

Lines:  y = 12, 23, 34, 45

top_clearance    = 12 - 9/2 = 12 - 4.5 = 7.5  ✓ (>= 6)
bottom_clearance = 58 - (45 + 7.5/2) = 58 - 48.75 = 9.25  ✓ (>= 6)
```

Both clearances exceed P=6. Padding is balanced (7.5 top, 9.25 bottom — the
small difference is because the title font is larger than body font, which is
expected and visually correct).

### Common Mistakes to Avoid

- **Eyeballing y-values** — Never pick y-values by feel. Always compute
  `box_center - total_span/2` first, then derive each line from that.
- **Placing title at a fixed offset** like `y=15` regardless of box height —
  this causes the content group to drift toward the bottom as boxes get
  shorter.
- **Forgetting the font-size half-height** — The text y-coordinate is the
  CENTER of the glyph. The top/bottom edges extend by font_size/2 beyond it.
  A line at y=52 in a height=58 box with 7.5px font has its bottom edge at
  y=55.75 — only 2.25px from the border. Always verify with Step 3.

## Floating Elements (Markers, Tooltips, Badges)

Any element that overlays the slide layout — tooltips, "we are here" markers,
callout badges, speech-bubble annotations — must be placed without overlapping
existing content. This is the second most common SVG slide mistake after
uneven padding.

### Overlap prevention rule

Before placing any floating element, compute its **full bounding box**
(rect + arrow tip + stroke width). Then verify it does not overlap with ANY
other element's bounding box. Remember: with `dominant-baseline="central"`,
a text glyph extends `font_size / 2` above and below its `y` coordinate.

**Minimum clearance between a floating element and any adjacent element: 4px.**

### Space insertion algorithm

When a floating element must sit between two vertical sections (e.g., a
marker between a subtitle and a bar chart):

```
needed   = element_height + arrow_extension + 2 × clearance
available = next_section_y - previous_element_bottom

if available < needed:
    delta = needed - available
    shift next_section and ALL downstream elements down by delta
    increase viewBox height by delta
```

This cascading shift applies to every `y`, `y1`, `y2`, `cy`, and polygon
point below the insertion gap. Missing even one element creates a visual
break — search the file for every numeric y-value and verify each was
either left unchanged (above the gap) or shifted by exactly `delta`.

### Post-placement checklist

After positioning a floating element, explicitly verify:

- [ ] No overlap with any text line, rect, circle, line, or polygon
- [ ] Arrow tip has >= 4px clearance to its target element
- [ ] Element body has >= 4px clearance to adjacent text above/below
- [ ] Element stays within the SVG viewBox bounds
- [ ] If the element is a speech bubble, it follows the 3-layer structure
      (rect → stroked arrow → cover polygon) from the Speech Bubble section

### Common mistakes

- **Placing a marker at a hardcoded y without checking surrounding text** —
  a "WE ARE HERE" badge at y=36 will overlap a subtitle at y=44. Always
  compute: `subtitle_bottom = subtitle_y + font_size/2`, then place the
  marker at `subtitle_bottom + clearance`.
- **Forgetting to cascade the shift** — inserting 20px of space for a marker
  but not shifting the elements below it by 20px. Every downstream y-value
  must be updated.
- **Using a simple rect+triangle without the 3-layer structure** — floating
  badges that act as speech bubbles must follow the same rect → stroked
  arrow → cover polygon pattern. A bare polygon without a cover will show
  a stroke seam.

## SVG Structure Template

Use this skeleton for every slide SVG. Note: replace the example values with
actual dimensions and colors for the specific slide.

```xml
<svg width="100%" viewBox="0 0 680 720" xmlns="http://www.w3.org/2000/svg">
<defs>
  <!-- One marker per arrow color — never use context-stroke -->
  <marker id="arrow-coral" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="#C0364A"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>

<style>
  /* Typography — Inter */
  .th { font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px; font-weight: 600; }
  .ts { font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 11px; font-weight: 400; }

  /* Color classes */
  /* Text must ONLY be dark (#16213E) or white (#FFFFFF) */
  .c-coral rect  { fill: #FDECEF; stroke: #C0364A; }
  .c-coral text  { fill: #16213E; }
</style>

<!-- Content here -->
</svg>
```

## Speech Bubble Text Blocks

Speech bubbles are rounded rectangles with a triangular pointer (arrow) that
indicates the speaker. Getting the arrow-to-rect junction right is the main
challenge — a visible stroke line at the seam looks broken.

### Structure (3 layers)

A speech bubble requires exactly three elements in this order:

1. **Rounded rect** — the bubble body with stroke
2. **Stroked arrow polygon** — the triangular pointer with matching stroke
3. **Cover polygon** — a slightly larger fill-only triangle that hides the
   rect's stroke at the junction

```xml
<!-- 1. Bubble body -->
<rect x="0" y="0" width="130" height="38" rx="8"
      fill="#E8F8E8" stroke="#27ae60" stroke-width="1"/>
<!-- 2. Arrow with stroke (visual outline) -->
<polygon points="-10,19 0,12 0,26"
         fill="#E8F8E8" stroke="#27ae60" stroke-width="1"
         stroke-linejoin="round"/>
<!-- 3. Cover polygon (hides rect stroke at junction) -->
<polygon points="-8,19 2,11 2,27" fill="#E8F8E8" stroke="none"/>
```

### Arrow placement rules

- **Base connects at x=0** (the rect's left edge), NOT inside the rect.
  Connecting at x > 0 makes the arrow look detached and floating.
- **Base y-range must be within the rect's flat edge** — for a rect with
  `rx=R`, the flat left edge runs from `y=R` to `y=height-R`. Keep the
  arrow base points inside this range.
- **Tip extends outward** by 8–12px (e.g., x=-10 for a left-pointing arrow).
- **Vertically centered** — the arrow tip y-coordinate should equal
  `height / 2`. The base points should be symmetric around the center.

### Cover polygon rules (critical)

The cover polygon prevents the rect's stroke from showing through at the
junction. It must:

- **Extend past the stroke** — its base x must be >= `stroke-width + 1`
  (e.g., x=2 for a 1px stroke). Using x=0 will leave a visible seam.
- **Be slightly taller than the stroked arrow** — extend the y-range by
  1–2px on each side (e.g., arrow at y=12,26 → cover at y=11,27).
- **Use the same fill as the rect** and `stroke="none"`.

### Arrow direction

Adjust the polygon points based on which side the arrow points from:

| Direction | Tip x     | Base x        | Cover base x      |
|-----------|-----------|---------------|--------------------|
| Left      | negative  | 0             | +2 (into rect)     |
| Right     | width + N | width         | width - 2          |
| Top       | center    | y=0           | y=+2               |
| Bottom    | center    | y=height      | y=height-2         |

### Common mistakes

- **Seam line**: Cover polygon base at x=0 doesn't hide the 1px stroke.
  Fix: extend to x=2.
- **Arrow in rounded corner zone**: Base points at y < rx or y > height-rx
  overlap with the curve. Fix: keep base within the flat edge region.
- **Arrow too small**: A 6px tip extension looks like a rendering glitch.
  Fix: use 8–12px for clear visual intent.

## Bullet Points in List Widgets

When a box or card contains a list of items (not paragraph text), always add
round bullet dots before each item. SVG has no native list support, so render
bullets manually with `<circle>` elements.

### How to render bullets

Place a small filled circle at the start of each line, vertically centered on
the text's y-coordinate. Then offset the text to the right:

```xml
<circle cx="14" cy="32" r="1.5" fill="#16213E"/>
<text x="20" y="32" dominant-baseline="central" class="box-text">List item</text>
```

Rules:
- **Bullet radius**: 1.5px (scales well at 7–9px font sizes)
- **Bullet cx**: same as the original text left padding (e.g., 10) + 4
- **Text x**: bullet cx + 6 (gives a clean gap between dot and text)
- **Bullet fill**: match the text fill color (e.g., `#16213E` for body text)
- **Bullet cy**: must equal the text `y` so `dominant-baseline="central"`
  aligns them perfectly

### When to use bullets

- List-style content inside boxes (e.g., "What agent did: deleted X, removed Y")
- Step-by-step sequences
- Feature/capability lists

### When NOT to use bullets

- Paragraph text that wraps across multiple `<text>` elements
- Single-line labels or titles
- Cards that are already visually separated (each with its own border/rect)

## Color Palette Convention

**Text must ONLY be dark (`#16213E`) or white (`#FFFFFF`)** — no colored
text. Use light tint backgrounds with matching shade strokes. Read
`references/color-palettes.md` for the full palette, CSS classes, and
color pairing rules.

## Fixing Existing SVGs

When an SVG renders with black boxes, missing colors, or invisible text:

1. Check for CSS classes without an embedded `<style>` — add one
2. Check for `var(--x)` — replace with explicit hex values
3. Check for `context-stroke` / `context-fill` — duplicate markers with
   explicit colors
4. Check text `y` positioning — recalculate with `box_y + height/2`
5. Check standalone text `fill` — add explicit fill attributes

## Additional Resources

### Reference Files

- **`references/color-palettes.md`** — Color palette with CSS classes,
  color pairing rules, and WCAG accessibility notes
- **`references/brand-typography.md`** — Inter font specification, weight
  mapping, and CSS class definitions

### Example Files

- **`examples/complete-slide.svg`** — Full working SVG slide demonstrating all
  rules: embedded styles, correct text centering, separate markers per color,
  explicit fills on standalone text, xmlns attribute. Use as a reference for
  the expected output quality.
