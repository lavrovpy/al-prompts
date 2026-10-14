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
metadata:
  version: "0.1.0"
---

# Text-to-SVG for Slides

Generate self-contained, portable SVG files for slides and diagrams that render
correctly in any environment — browsers, Miro, Figma, Notion, email clients,
and other tools that strip or ignore external stylesheets.

## Self-Contained SVGs

Every SVG this skill produces is fully self-contained, because the
renderers it is meant for (Miro, Notion, Google Slides, email clients) have
no access to external CSS, CSS custom properties, or modern SVG features.
Anything that leans on them shows up as black boxes, missing colors, or
invisible text.

### Checklist before finishing

Verify all of the following:

1. **Embedded `<style>` block** — Define all CSS classes inside the SVG's
   `<style>` element rather than an external stylesheet.
2. **No `var(--x)` references** — Replace every CSS custom property with an
   explicit color value (e.g., `var(--b)` → `#16213E`).
3. **No `context-stroke` or `context-fill`** — Most SVG renderers do not
   support them. Create separate `<marker>` definitions
   with hardcoded colors for each stroke color needed.
4. **Explicit `fill` on standalone text** — Text elements outside a styled `<g>`
   must have an explicit `fill` attribute (default SVG fill is black).
5. **Add `xmlns="http://www.w3.org/2000/svg"`** — Required for SVGs used
   outside HTML documents.

## Layout Rules

Before placing text in a box, a floating marker, a speech bubble, or a list,
read `references/layout-rules.md`. It holds the padding arithmetic, the
overlap checks, the 3-layer speech-bubble structure, and the bullet
convention. Uneven padding and overlapping floating elements are the two
most common SVG slide mistakes, and both come from eyeballing coordinates
instead of computing them.

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
  /* Text is dark (#16213E) or white (#FFFFFF), never colored */
  .c-coral rect  { fill: #FDECEF; stroke: #C0364A; }
  .c-coral text  { fill: #16213E; }
</style>

<!-- Content here -->
</svg>
```

## Color Palette Convention

Text is dark (`#16213E`) or white (`#FFFFFF`), never colored, so it stays
legible on every tint. Use light tint backgrounds with matching shade strokes. Read
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

- **`references/layout-rules.md`** — Padding arithmetic, floating-element
  overlap checks, speech-bubble structure, and bullet rendering
- **`references/color-palettes.md`** — Color palette with CSS classes,
  color pairing rules, and WCAG accessibility notes
- **`references/brand-typography.md`** — Inter font specification, weight
  mapping, and CSS class definitions

### Example Files

- **`examples/complete-slide.svg`** — Full working SVG slide demonstrating all
  rules: embedded styles, correct text centering, separate markers per color,
  explicit fills on standalone text, xmlns attribute. Use as a reference for
  the expected output quality.
