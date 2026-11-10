---
name: intent-rich-pr
description: Write the title and description of a GitHub pull request or GitLab merge request, and open it. Purpose, the problem the change exists to solve, is required and comes first; refuse to open the PR/MR when no purpose is given or inferable. Review focus, the 1–3 places a human must still read, is required. Screenshots are required whenever the diff changes something a person sees. Use when drafting, creating, opening, or submitting a PR, MR, or its description, including each PR in a stack.
---

# Intent-Rich PR

An agent can draft a pull request. The person who opens it is responsible for what it says, so the draft must be something they would defend in review. The failure mode this avoids is described at [dontpastetheai.com](https://dontpastetheai.com/).

## Gate (before any PR/MR exists)

State the **purpose** in one or two sentences: the problem this change exists to solve, including what goes wrong if it does not merge.

Sources, in order:

1. The user, in this conversation.
2. The linked issue or ticket's problem statement, rather than the solution it proposes. Fetch GitHub issues with `gh issue view`, GitLab ones with `glab issue view`. Never invent ticket context.
3. The diff, when the problem is obvious from the code.

An account of what was built, which files moved, or which tests passed describes the solution, so it does not pass the gate. If no source gives a purpose, ask the user and do not open the PR/MR until you have one.

Done when: a reviewer who never saw the ticket can answer "why does this need to land?" from the Summary alone.

## Body

Two required sections, Summary and Review focus, plus Screenshots when the diff changes anything a person sees. Use the repo's PR/MR template when it has one, keeping these sections inside it. Write in [Google developer documentation style](https://developers.google.com/style); Summary may say "we" for the team's problem.

Describe the change as the diff against the base branch shows it. In a stack, that base is the PR below, so each body covers only its own step. Every claim points at something in that diff.

Read [examples.md](references/examples.md) before drafting and rewrite any part that resembles a Bad example.

### Summary

Two to five sentences in up to three short paragraphs separated by blank lines: the purpose, then one sentence on what you did, then what is deliberately out of scope when a reviewer would otherwise ask why it is missing. Put the issue link at the end of the first paragraph when there is one.

The blank lines matter: PR lists and notification mail truncate the description, so a reviewer often sees only the first paragraph. Keep the purpose there by itself.

### Review focus

Automated review covers mechanical defects; this section names what still needs a person. Write one to three bullets, each naming a path and the decision waiting there: a trade-off, an irreversible step, a critical path to trace, a test that was rewritten or weakened, or a part you are unsure about. When you cannot tell which places matter most, write those open questions instead.

Add one Mermaid diagram in a `mermaid` fence when a picture makes a decision faster, such as a request path or a before-and-after of control flow. Name generated files, lockfiles, and pure reformats as safe to skim.

Done when: a reviewer can open those paths first and know what question they are answering there. When every part of the diff needs judgment, split it into a stack instead of sharpening this section.

### Screenshots

Required when the diff changes a UI, a rendered page or document, an email, a chart, or terminal output a user reads. Show before and after for changed screens, and the after state alone for new ones. Capture them yourself by running the app with the browser or screenshot tool you have; the dev server is usually already running.

- GitLab: upload each image with the project uploads API (`POST /projects/:id/uploads`) and paste the returned `markdown` into the section.
- GitHub has no API for PR attachments. Open the PR as a draft with a `## Screenshots` section that lists each missing shot as `<!-- TODO: after: settings page, dark mode -->`, save the captures locally, and report their paths so the user can drag them in and mark the PR ready.

Omit the section when nothing visible changed.

## Open the PR/MR

- Title: name the cause, what is wrong in the files this diff changes, in 72 characters or fewer, with the ticket key when there is one. The symptom goes in Summary; the mechanism stays in the diff.
- Base: the branch below in a stack, otherwise the repo's default branch unless the user named another.
- GitHub: `gh pr create --title <title> --body-file <file>`, adding `--base <branch>` in a stack and `--draft` when screenshots are owed.
- GitLab: `glab mr create --title <title> --description "$(cat <file>)" --yes`, adding `--target-branch <branch>` in a stack and `--draft` when screenshots are owed.
- Report the URL, base and head branches, draft status, and any screenshots still owed.

When the user asked only for a description, reply with the title and body in one markdown block and stop.

## Rules

- Never claim that a ticket, issue, test, or review exists unless you verified it.
- No validation lists, test counts, or chronology of the work: they describe the solution, and CI shows the checks.
