# PR Body Guide

Use this reference when drafting an intent-rich pull request description.

## Template

```md
## Reviewer context

Please read this description before reviewing the diff. The important context is: <one or two sentences about what reviewers should understand first>.

## Motivation

<Explain why this change exists. Include the original user request, ticket, issue, incident, or product/design motivation.>

Issue/ticket: <link or "None">

## Decision rationale

<Summarize reviewer-facing reasoning: important decisions, tradeoffs, rejected options, course corrections, and assumptions. Do not include raw hidden chain-of-thought.>

## What changed

- <Concrete change 1>
- <Concrete change 2>
- <Concrete change 3>

## Validation

- <Command/check/result>
- <Command/check/result>

## Risk or follow-up

<Optional. Include known gaps, manual review needs, or deferred work. Omit if not useful.>
```

## Example

```md
## Reviewer context

Please read this description before reviewing the diff. The important part of this change is not just the wording edits: it is the intent behind making the image prompt safer for language-learning content.

## Motivation

The language-learning infographic prompt asks an image model to create an educational vocabulary poster. That means the output is only useful if the in-image text is correct, legible, and intentionally selected.

Issue/ticket: None

The earlier one-pass prompt let the model invent vocabulary, translations, phrases, layout, and final rendered text all at once. That creates two practical review risks:

- A generated poster can contain wrong translations, missing accents, spelling mistakes, or mixed-up languages, which is a correctness failure for a learning aid.
- A 16:9 poster can easily become too dense when the prompt asks for nouns, actions, concepts, phrases, and sentences without a strict text budget.

## Decision rationale

The fix uses a two-step workflow instead of trying to make the final image generation prompt carry all correctness responsibility:

1. The assistant first produces an exact copy deck and asks for approval.
2. The image is generated only after approval.
3. The approved copy must be used exactly, without paraphrasing, extra translation, or improvised in-image text.

This makes the language content inspectable before it becomes pixels. It also gives future code-review or prompt-review agents the real design intent: the prompt is optimized for educational correctness and legibility, not maximum vocabulary coverage.

## What changed

- Added missing-input handling for target language, native language, and topic placeholders.
- Added an approval-first copy deck workflow.
- Required the copy deck to be the exact final in-image text.
- Added strict text-density limits for sections, vocabulary items, and phrases.
- Updated the README example to mention approving the copy deck before generating the poster.

## Validation

- Ran `git diff --check`.
- Confirmed the branch is clean and pushed.
```

## Decision Rationale Guidance

Include rationale when it changes how reviewers should interpret the diff, for example:

- A ticket requested one thing, but implementation required a narrower or safer path.
- The agent chose a conservative tradeoff to reduce risk.
- A first approach was abandoned after discovering repo constraints.
- The diff looks indirect because it preserves compatibility or existing conventions.
- A test or validation gap remains and reviewers should know why.

Avoid:

- Raw hidden reasoning.
- Long chronological narration.
- Generic statements like "this improves quality" without explaining why.
- Claims about issue context or validation that were not verified.
