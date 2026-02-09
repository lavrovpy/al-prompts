---
name: nmt-test
description: Generate complete NMT (Національний мультипредметний тест) standardized educational assessment tests following the official Ukrainian exam format. Use when the user wants to create NMT practice tests, exam papers, or standardized assessments. Supports multiple disciplines with discipline-specific structures: history (Історія України), mathematics (Математика), Ukrainian language (Українська мова), biology (Біологія), physics (Фізика), and other subjects by analogy. Each discipline has its own question types, scoring, and quantity — read the corresponding example file before generating.
---

# NMT Test Generator

Generate high-quality NMT (Національний мультипредметний тест) practice tests following the official Ukrainian standardized exam format. Output as a single self-contained artifact/canvas in Markdown.

## Step 1: Determine Discipline & Configuration

Ask the user or infer from context:

```yaml
discipline: ""              # REQUIRED: history | math | ukrainian-language | biology | chemistry | physics | geography | other
topic: "general"            # specific topic or "general" for full coverage
language: "ukrainian"       # output language
answer_labels: "cyrillic"   # "cyrillic" (А,Б,В,Г,Д) | "latin" (A,B,C,D,E)
difficulty: "standard"      # "easy" | "standard" | "advanced"
include_answer_key: true
```

## Step 2: Load Discipline-Specific Structure

**Before generating any questions**, read the corresponding example file from `examples/` to understand the exact test structure, question types, scoring, and format for that discipline:

- **History** → [examples/history.md](examples/history.md) — 30 questions, 54 pts max
- **Mathematics** → [examples/math.md](examples/math.md) — 22 questions, 32 pts max
- **Ukrainian Language** → [examples/ukrainian-language.md](examples/ukrainian-language.md) — 30 questions, 45 pts max
- **Biology** → [examples/biology.md](examples/biology.md) — 30 questions, 46 pts max
- **Physics** → [examples/physics.md](examples/physics.md) — 20 questions, 32 pts max

For disciplines without a dedicated example file, use the closest analogue:
- Chemistry → adapt the **biology** structure (single-choice/4opt + matching + three-column select)
- Geography, Law, other humanities → adapt the **history** structure (single-choice/4opt + matching + sequencing + multi-select)
- English, other languages → adapt the **ukrainian-language** structure

Each example file contains:
1. Test overview (total questions, max score)
2. Question types table with exact quantities, option counts, and scoring
3. Section-by-section format with real NMT example questions
4. Design notes for question and distractor construction

## Step 3: Generate Questions

Follow the structure and question types from the loaded example file exactly. Key rules:

### Difficulty Distribution
- Easy (direct recall/application): 20-25%
- Medium (understanding + reasoning): 50-60%
- Difficult (multi-step, combining concepts): 20-25%

### Universal Quality Rules
- Precise, unambiguous language in Ukrainian
- Each question tests ONE main concept or skill
- Avoid double negatives
- Distractors must be plausible — based on real misconceptions, not absurd options
- Options should be similar in length and structure
- Cover the required curriculum breadth across questions

### Discipline-Specific Rules

**Sciences/Math:** Include diagrams described textually (e.g., "[Графік: парабола y=x² з вершиною в точці (0,0)]"). Provide reference materials section with formulas and constants.

**History/Humanities:** Use primary source excerpts (quotes, documents). Describe visual sources textually (e.g., "[Фото: будівля Верховної Ради]", "[Карта: територія Гетьманщини]"). Cover the full chronological span.

**Languages:** Include shared text passages for text-based questions. Test real grammatical pitfalls students commonly encounter.

## Step 4: Format Output

For detailed output formatting, see:
- [references/output-format.md](references/output-format.md) — output template and formatting guide
- [references/question-types.md](references/question-types.md) — cognitive levels and distractor design

### Output Structure
```
# [DISCIPLINE] — НМТ [Year]
## Демонстраційний варіант

[Section instruction banner for each section]

[Questions numbered sequentially]

---
## Довідкові матеріали (if applicable)
[Reference sheet for math/science]

---
## Відповіді
[Answer key table]
```
