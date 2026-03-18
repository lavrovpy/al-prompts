# Typography for SVG Slides

## Primary Typeface: Inter

Inter is the primary typeface (Google Font, free). Use it for all
text in SVG slides.

### Font Weight Mapping

| Usage      | Weight name | Weight value | Example                    |
|------------|-------------|--------------|----------------------------|
| Headlines  | SemiBold    | 600          | Section titles, stat numbers|
| Headlines  | Bold        | 700          | Slide titles               |
| Body text  | Regular     | 400          | Descriptions, list items   |

### SVG Fallback Stack

```
'Inter', 'Segoe UI', sans-serif
```

Use this fallback in all `font-family` declarations. Inter will render
when available (Google Fonts); Segoe UI covers Windows; sans-serif is the
final fallback.

## CSS Classes for SVG `<style>` Blocks

```css
/* Title/heading text */
.th { font-family: 'Inter', 'Segoe UI', sans-serif;
      font-size: 13px; font-weight: 600; }

/* Subtitle/body text */
.ts { font-family: 'Inter', 'Segoe UI', sans-serif;
      font-size: 11px; font-weight: 400; }
```

## Secondary Typeface: Noto Sans

Noto Sans is used ONLY for Cyrillic and Georgian scripts. Do not use it for
Latin text.

## Design Principles

- **"Clear over clever"** — prioritize legibility over stylistic effects
- Clean, modern, minimal
- Use sufficient contrast (see color-palettes.md for WCAG scores)
