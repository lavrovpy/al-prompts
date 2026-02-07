---
name: nmt-test
description: Generate complete standardized educational assessment tests with single-choice, matching, and numerical answer questions. Use when the user wants to create exam papers, practice tests, or standardized assessments for any discipline (physics, chemistry, math, history, languages, etc.).
---

# Educational Assessment Question Generator

Generate high-quality standardized test questions. Output as a single self-contained artifact/canvas in Markdown.

## User Configuration

Accept these settings from the user (defaults shown):

```yaml
output_format: "artifacts"        # "artifacts" | "canvas"
language: "ukrainian"             # any language
answer_labels: "latin"            # "cyrillic" (А,Б,В,Г) | "latin" (A,B,C,D)
discipline: "physics"             # subject area
topic: "general"                  # specific topic or "general"
difficulty: "standard"            # "easy" | "standard" | "advanced"
single_choice_count: 12
matching_count: 2
numerical_count: 6
include_diagrams: true
include_reference_sheet: true
include_answer_key: true
```

## Test Structure

| Type | Default Qty | Points per Q | Total |
|------|------------|-------------|-------|
| Single-choice (4 options) | 12 | 0 or 1 | 12 |
| Matching (4 items → 5 options) | 2 | 0-4 | 8 |
| Short numerical answer | 6 | 0 or 2 | 12 |
| **TOTAL** | **20** | — | **32** |

## Question Type Specifications

For detailed specs on each question type, see:
- [references/question-types.md](references/question-types.md) — format, cognitive levels, distractor design, scoring
- [references/output-format.md](references/output-format.md) — output structure template and discipline adaptation guide

## General Guidelines

### Difficulty Distribution
- Easy (direct recall/application): 20-25%
- Medium (understanding + reasoning): 50-60%
- Difficult (multi-step, combining concepts): 20-25%

### Language and Clarity
- Precise, unambiguous language
- Define symbols/abbreviations on first use
- Avoid double negatives
- Each question tests ONE main concept or skill

### Quality Checklist
Before finalizing, verify:
- All questions complete and properly numbered
- Each single-choice has exactly 4 options with 1 correct
- Each matching has 4 items and 5 options
- All numerical answers achievable with given data
- Units specified for all physical quantities
- Diagrams/graphs clear and properly labeled
- Content covers required curriculum areas
- Answer key is complete and accurate
- Reference materials include all necessary data
