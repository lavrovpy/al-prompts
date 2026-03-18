# Color Palette for SVG Slides

All SVG slides must use only these colors. **Copy/text must ONLY be black
(#16213E) or white (#FFFFFF)** — no colored text.

## Primary Palette

| Name  | Hex       | Usage                            |
|-------|-----------|----------------------------------|
| White | `#FFFFFF` | Backgrounds, text on dark        |
| Dark  | `#16213E` | Text, borders, dark backgrounds  |
| Coral | `#E94560` | Signature accent, hero highlight |

## Secondary Palette

| Name      | Hex       | Usage                        |
|-----------|-----------|------------------------------|
| Off-White | `#EDF2F7` | Cool gray background         |
| Teal      | `#2EC4B6` | Secondary accent             |
| Amber     | `#F4A261` | Secondary accent             |

## Tints (light backgrounds for boxes/cards)

| Name       | Hex       | Usage                         |
|------------|-----------|-------------------------------|
| Coral Tint | `#FDECEF` | Light coral box background    |
| Teal Tint  | `#E0F7F5` | Light teal box background     |
| Amber Tint | `#FFF3E0` | Light amber box background    |

## Accessible Shades (strokes/borders — WCAG AA on white)

| Name        | Hex       | WCAG ratio | Usage               |
|-------------|-----------|------------|----------------------|
| Coral Shade | `#C0364A` | 4.5        | Strokes, borders     |
| Teal Shade  | `#1B8F84` | 3.5        | Strokes, borders     |
| Amber Shade | `#B87A2E` | 3.0        | Strokes, borders     |

## Ready-to-Use CSS Classes

### On white/light backgrounds (default)

```css
.c-coral rect    { fill: #FDECEF; stroke: #C0364A; }
.c-coral text    { fill: #16213E; }

.c-teal rect     { fill: #E0F7F5; stroke: #1B8F84; }
.c-teal text     { fill: #16213E; }

.c-amber rect    { fill: #FFF3E0; stroke: #B87A2E; }
.c-amber text    { fill: #16213E; }

.c-neutral rect  { fill: #EDF2F7; stroke: #16213E; }
.c-neutral text  { fill: #16213E; }
```

### On dark backgrounds (dark #16213E)

When the slide background is dark, use the brighter primary/secondary
colors directly — do not use Shades.

```css
.c-coral-dark rect   { fill: #16213E; stroke: #E94560; }
.c-coral-dark text   { fill: #FFFFFF; }

.c-teal-dark rect    { fill: #16213E; stroke: #2EC4B6; }
.c-teal-dark text    { fill: #FFFFFF; }

.c-amber-dark rect   { fill: #16213E; stroke: #F4A261; }
.c-amber-dark text   { fill: #FFFFFF; }
```

## Color Pairing Rules

When combining colors in a single composition:

1. **Use only ONE bright color** (Coral, Teal, or Amber) per composition
2. **Coral Tint is universal** — it pairs with Coral, Teal, or Amber
3. **Teal Tint** pairs ONLY with Teal (not Amber or Coral)
4. **Amber Tint** pairs ONLY with Amber (not Teal or Coral)
5. Pair a bright color with its corresponding tint, Coral Tint, or a neutral
6. **Do not layer patterns** on top of each other or add textures

### Valid combinations

| Bright color | Can pair with                              |
|--------------|--------------------------------------------|
| Coral        | Coral Tint, Off-White, White, Dark         |
| Teal         | Teal Tint, Coral Tint, Off-White, White    |
| Amber        | Amber Tint, Coral Tint, Off-White, White   |

## Neutral Colors

For titles, subtitles, and dividers outside colored groups:

| Element        | Value                       | Usage                      |
|----------------|-----------------------------|----------------------------|
| Title text     | `#16213E`                   | Main headings              |
| Subtitle text  | `#16213E`                   | Secondary/descriptive text |
| Divider lines  | `#16213E` with `opacity=0.2`| Horizontal separators      |
| Bullet dots    | `#16213E`                   | List markers               |
