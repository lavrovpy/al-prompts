---
name: language-learning-infographic
description: Generate clean, illustrated vocabulary infographic posters for language learning. Use when the user wants to create a visual study sheet, illustrated vocabulary poster, or language learning infographic for a target language and topic.
---

# Language Learning Infographic Generator

Generate clean, friendly, illustrated language-learning infographic posters in a polished language-book / textbook style.

## Input Parameters

Determine the following configuration with the user:

- **Target language:** `[TARGET_LANGUAGE]` (Required)
- **Native / translation language:** `[NATIVE_LANGUAGE]` (Required)
- **Topic:** `[TOPIC]` (e.g., cafe, supermarket, travel, gym, office, doctor visit, weather, apartment, hobbies; if unspecified, choose a common everyday topic)

If the target or native language is unspecified, ask for it before proceeding.

## Two-Step Workflow

1. **Step 1 — Create and Approve Copy Deck:**
   - Draft the copy deck first and present it to the user for approval.
   - Do not generate the poster image until the user approves the copy deck.
2. **Step 2 — Generate Poster Image:**
   - Once approved, generate the image using the approved copy deck verbatim.
   - Do not add, remove, paraphrase, translate, or improvise in-image text.

## Copy Deck Guidelines

- **Audience:** Learners whose native language is `[NATIVE_LANGUAGE]` learning `[TARGET_LANGUAGE]`.
- **Vocabulary:** High-frequency, natural words and phrases. Avoid rare, academic, or overly formal vocabulary.
- **Accuracy:** Correct grammar, spelling, accents, and diacritics in both languages.
- **Hierarchy:** `[TARGET_LANGUAGE]` text first (bold and visually dominant), followed by `[NATIVE_LANGUAGE]` translation.

### Copy Deck Limits

- **1 Title:** In `[TARGET_LANGUAGE]`, short enough for a single line, based on the topic. Do not use English scaffolds like "Vocabulary:" unless English is the target language.
- **Maximum 4 content sections.**
- **Maximum 5 vocabulary items per section.**
- **Maximum 1 short useful phrase or sentence per section.**
- **No paragraphs.** Prioritize legibility and correctness over volume.

## Visual Design & Layout Guidelines

- **Canvas:** Clean 16:9 landscape layout.
- **Title Area:** Dedicated top banner across the full width, clearly separated from the content area with generous empty space below.
- **Content Grid:** Balanced grid of rounded, color-coded section boxes with safe margins around the entire image.
- **Illustrations:** Polished textbook infographic style. Small spot illustrations and icons next to words and phrases (avoid a single large central illustration that dominates the page).
- **Typography:** Readable typography with strong contrast. `[TARGET_LANGUAGE]` words bold and visually dominant; translations smaller but easy to read. Leave ample spacing so section titles, vocabulary, and translations never overlap or collide.
- **Color Palette:** Bright, clean colors with a flat-vector or soft cartoon aesthetic.

## Negative Constraints

Do not include subtitles, taglines, watermarks, unrelated logos, random filler text, misspellings, large decorative center scenes, colliding titles/content, cropped text, overlapping boxes, or mixed-up languages.
