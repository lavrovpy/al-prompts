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
   explicit color value (e.g., `var(--b)` → `#999`).
3. **No `context-stroke` or `context-fill`** — These are modern CSS properties
   unsupported in most SVG renderers. Create separate `<marker>` definitions
   with hardcoded colors for each stroke color needed.
4. **Explicit `fill` on standalone text** — Text elements outside a styled `<g>`
   must have an explicit `fill` attribute (default SVG fill is black).
5. **Add `xmlns="http://www.w3.org/2000/svg"`** — Required for SVGs used
   outside HTML documents.

## Text Centering Inside Boxes

Incorrect text centering is the most common SVG slide mistake. Follow these
rules precisely.

### Single-Line Text

When using `dominant-baseline="central"` (always use it), the `y` coordinate
IS the vertical center of the text. To center text inside a `<rect>`:

```
text_x = rect_x + rect_width / 2      (with text-anchor="middle")
text_y = rect_y + rect_height / 2      (NOT rect_y + height - some_offset)
```

Example — rect at y=136, height=32:
- Correct:   `text y="152"` (136 + 16)
- Incorrect: `text y="156"` (off by 4px — looks subtle but compounds)

### Two-Line Text

Center the pair so the midpoint of the two y-coordinates equals the box center:

```
box_center = rect_y + rect_height / 2
line1_y = box_center - half_line_gap
line2_y = box_center + half_line_gap
```

Example — rect at y=652, height=44, line gap=16:
- box_center = 674
- line1 y = 674 - 8 = 666
- line2 y = 674 + 8 = 682

### Multi-Line Text (3+ lines)

Keep original inter-line spacing. Calculate the midpoint of first and last
line y-values, then shift the entire group so that midpoint equals the box
center:

```
content_midpoint = (first_line_y + last_line_y) / 2
shift = box_center - content_midpoint
Apply shift to ALL lines in the group.
```

### Common Centering Mistake

Never eyeball y-values or use arbitrary offsets like `box_y + height - 12`.
Always compute `box_y + height / 2`. With `dominant-baseline="central"`, the
math is exact.

## SVG Structure Template

Use this skeleton for every slide SVG. Note: replace the example values with
actual dimensions and colors for the specific slide.

```xml
<svg width="100%" viewBox="0 0 680 720" xmlns="http://www.w3.org/2000/svg">
<defs>
  <!-- One marker per arrow color — never use context-stroke -->
  <marker id="arrow-teal" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="#0F6E56"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>

<style>
  /* Typography — define once here, not in external CSS */
  .th { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 13px; font-weight: 600; }
  .ts { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 11px; font-weight: 400; }

  /* Color classes — light bg, dark stroke/text */
  .c-teal rect  { fill: #E8F5F0; stroke: #0F6E56; }
  .c-teal text  { fill: #0F6E56; }
</style>

<!-- Content here -->
</svg>
```

## Color Palette Convention

When creating slide diagrams with semantic colors, use light backgrounds with
matching darker strokes and text. Read `references/color-palettes.md` for
ready-to-use palettes with teal, red, coral, amber, green, blue, and purple.

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

- **`references/color-palettes.md`** — Ready-to-use semantic color palettes
  and typography class definitions

### Example Files

- **`examples/complete-slide.svg`** — Full working SVG slide demonstrating all
  rules: embedded styles, correct text centering, separate markers per color,
  explicit fills on standalone text, xmlns attribute. Use as a reference for
  the expected output quality.
