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

## Review focus

<State the blast radius and where reviewers should spend attention: risky files, user-facing behavior, data/security paths, test rewrites, CI changes, or why this is low-risk. Treat AI review findings as signals, not final approval.>

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

## Review focus

Please review the prompt flow rather than only the wording diff. The important risk is whether the workflow still allows unapproved or improvised educational text into the final image. The validation is light, so this should get a human prompt-review pass before being treated as a stable content-generation pattern.

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
- The implementation is agent-authored and the useful plan, assumptions, or rejected alternatives should be preserved for the reviewer.

Avoid:

- Raw hidden reasoning.
- Long chronological narration.
- Generic statements like "this improves quality" without explaining why.
- Claims about issue context or validation that were not verified.

## Review Focus Guidance

Use this section to help reviewers allocate scarce attention.

Include:

- Blast radius: who or what is affected if this is wrong.
- Load-bearing areas: auth, payments, security, privacy, migrations, data integrity, prompts with untrusted input, CI, or core business logic.
- Review friction: large diffs, many touched files, generated code, unclear ownership, or broad test rewrites.
- Test scrutiny: whether assertions changed, tests were removed/skipped, lint or coverage thresholds moved, or CI behavior changed.
- Review posture: low-risk glance, normal human review, targeted owner review, security review, or multiple review signals.

Avoid:

- Treating passing tests or AI review approval as proof that the change is understood.
- Asking reviewers to inspect everything equally.
- Hiding known validation gaps in a generic risk section.
