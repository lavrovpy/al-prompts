# Color Palettes for SVG Slides

Ready-to-use semantic color palettes. Each palette provides `fill` (light
background), `stroke` (border), and `text fill` (dark foreground) values.

## Standard Semantic Palette

Designed for diagrams that contrast positive/clean (teal/green) with
negative/polluted (red/coral) states, plus neutral highlights (amber).

### Teal (positive, clean, solutions)

```css
.c-teal rect  { fill: #E8F5F0; stroke: #0F6E56; }
.c-teal text  { fill: #0F6E56; }
```

- Background: `#E8F5F0` (light mint)
- Stroke/Text: `#0F6E56` (deep teal)
- Arrow color: `#0F6E56`

### Green (success, result)

```css
.c-green rect { fill: #E4F7E8; stroke: #0F6E56; }
.c-green text { fill: #0F6E56; }
```

- Background: `#E4F7E8` (light green)
- Stroke/Text: `#0F6E56` (deep teal)

### Red (negative items, errors)

```css
.c-red rect   { fill: #FDECEB; stroke: #C0392B; }
.c-red text   { fill: #993C1D; }
```

- Background: `#FDECEB` (light rose)
- Stroke: `#C0392B` (crimson)
- Text: `#993C1D` (dark brick)

### Coral (negative container)

```css
.c-coral rect { fill: #FDF0EB; stroke: #993C1D; }
.c-coral text { fill: #993C1D; }
```

- Background: `#FDF0EB` (light peach)
- Stroke/Text: `#993C1D` (dark brick)
- Arrow color: `#993C1D`

### Amber (stats, highlights, warnings)

```css
.c-amber rect { fill: #FEF5E7; stroke: #B7791F; }
.c-amber text { fill: #92610A; }
```

- Background: `#FEF5E7` (light cream)
- Stroke: `#B7791F` (golden)
- Text: `#92610A` (dark amber)

## Neutral Colors

For titles, subtitles, and dividers outside colored groups:

| Element            | Color     | Usage                         |
|--------------------|-----------|-------------------------------|
| Title text         | `#1A1A1A` | Main headings                 |
| Subtitle text      | `#555555` | Secondary/descriptive text    |
| Divider lines      | `#999999` | Horizontal separators         |

## Alternative Palettes

### Blue/Indigo (information, neutral comparison)

```css
.c-blue rect  { fill: #EBF1FD; stroke: #2B5797; }
.c-blue text  { fill: #1E3A5F; }
```

### Purple (creative, premium)

```css
.c-purple rect { fill: #F3ECFB; stroke: #6B3FA0; }
.c-purple text { fill: #4A2D6F; }
```

### Gray (disabled, inactive)

```css
.c-gray rect  { fill: #F2F2F2; stroke: #888888; }
.c-gray text  { fill: #555555; }
```
