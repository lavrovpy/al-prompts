A personal library of AI prompts and [Agent Skills](https://agentskills.io/specification) for writing, interview prep, translation, language learning, and education.

Most tools in this repo are available in **two forms**:

- **Prompts** (`prompts/`) — standalone system prompts you can copy-paste into any AI chat (ChatGPT, Claude, etc.). They follow a two-step **Prompt Priming** approach: the assistant first acknowledges the instructions and asks for input, then processes it using the specified format.
- **Skills** (`skills/`) — the same tools packaged as [Agent Skills](https://agentskills.io/specification) (each containing a `SKILL.md` file), installable in agent tools.
Some workflows are skill-only when they depend on agent context, repository state, or tool usage.

## Installing Skills

### 1) Manual install (clone + copy)

Clone the repository, then copy one or more skill folders from `skills/` to the local skills directory used by your tool.

```bash
git clone https://github.com/lavrovpy/al-prompts.git
cp -R al-prompts/skills/<skill-name> <your-tool-skills-directory>/
```

### 2) Claude Code plugin

Add the marketplace and install the plugin:

```
/plugin marketplace add lavrovpy/al-prompts
/plugin install alavreniuk-skills@alavreniuk-skills
```

After installation, skills are available as slash commands namespaced by the plugin (e.g. `/alavreniuk-skills:interview-questions-creator`; the bare `/interview-questions-creator` also works when no other command uses that name).

Third-party marketplaces don't auto-update by default. To update, run `/plugin`, open the **Marketplaces** tab, select `alavreniuk-skills`, and choose **Update marketplace** (or **Enable auto-update** to keep it current). From a shell:

```bash
claude plugin marketplace update alavreniuk-skills
claude plugin update alavreniuk-skills@alavreniuk-skills
```

### 3) Codex

Use Codex's `skill-installer` to install skills from this repository (GitHub repo/path installs are supported):

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo lavrovpy/al-prompts --path skills/<skill-name>
```

Or use a GitHub URL:

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --url https://github.com/lavrovpy/al-prompts/tree/main/skills/<skill-name>
```

After installing a skill in Codex, restart Codex to pick up new skills.

If you want to use skills with another tool, check that tool's documentation.

## Skill-only workflows

- `skills/ai-setup-audit`: Audit every AI coding tool on the machine (Claude Code, Codex, Cursor, agent CLIs, IDE MCP configs): usage evidence, plaintext secrets, blanket permissions, broken skill chains, duplicated or drifted skills, context cost, stale versions, and leftovers. You approve each fix, it applies only those, then reports before/after. A read-only `scripts/inventory.py` does the mechanical survey.
  - Example: Run `/ai-setup-audit` (or `/ai-setup-audit security only`); get a ranked DELETE / UPDATE / CHANGE / KEEP list with evidence, then a report of what changed.
- `skills/boil-the-ocean`: Hunt for performance wins at every layer, from algorithms to hardware to the requirement itself, extreme measures included. Measures a baseline, profiles, then returns three proposals that differ in kind, each with expected gain, cost, and a first step.
  - Example: Run `/boil-the-ocean the search endpoint`; get three ranked proposals, the last one radical, plus a one-line list of the other levers found.
- `skills/intent-rich-pr`: Create GitHub pull requests with descriptions that preserve motivation, issue/ticket links, reviewer-facing decision rationale, diff summary, and validation context.
- `skills/self-reflection`: Retro over a repo's last coding-agent sessions (Claude Code and Codex, worktrees included). Finds detours, where an agent took too long to reach a file, command, or convention; stale docs it trusted; and code that misleads agents: sprawling files, look-alike module names, dead code. Proposes fixes such as navigation pointers, doc corrections, automated checks, and splitting, renaming, or deleting that code.
  - Example: Run `/self-reflection` in a repo; get candidates ranked by how many tool calls each would have saved, each backed by a quote from the session.
- `skills/study-questions`: Generate closed-book study questions from course material and record an answer key in a `study-log.md` next to the material. Serves questions that are due for review before new ones.
  - Example: Point it at a course module; get 5-7 questions (how, why, compare, apply, find the error) plus a line listing concepts not covered this round.
- `skills/study-coach`: Grade answers to those questions against the course material, quote the source for each correction, and schedule the next review in `study-log.md` (1, 3, 7, 21 days).
  - Example: Give it a question ID and your answer; get a score, hints on the first attempt, and the full answer with the source quote after the second.

## Prompts

- `prompts/editor.md`: Senior English editor and writing coach for polishing professional text.
  - Example: Paste a draft email or Slack message; get a revised version plus a change summary and rating.
- `prompts/interview-coach.md`: FAANG-style interview coach for feedback on technical interview answers.
  - Example: Provide an interview question and your answer; get a score, strengths, and improvement hints.
- `prompts/interview-questions-creator.md`: FAANG-style interviewer that generates high-signal questions from provided materials.
  - Example: Attach a design doc or study notes; receive 5-7 deep-dive questions.
- `prompts/interview-scorecard.md`: Technical recruiter assistant that turns raw interview notes into a structured internal scorecard with hiring recommendation.
  - Example: Paste shorthand interview notes; get objective sections for strengths, gaps, seniority, and pass/fail decision.
- `prompts/notes-verification-assistant.md`: Academic verifier that audits notes for accuracy and rewrites them for study.
  - Example: Paste study notes; get an audit and a revised, high-density version.
- `prompts/translator-en-ukr.md`: English ↔ Ukrainian translator with nuance and context handling.
  - Example: Paste text in English or Ukrainian; get a fluent translation with nuance notes.
- `prompts/language-learning-infographic.md`: Image-generation prompt for a clean, illustrated vocabulary infographic poster in a polished language-book style.
  - Example: Set target language, native language, and a topic (e.g. cafe); approve the copy deck, then get a 16:9 color-coded poster with bold target words, translations, and useful phrases.
- `prompts/experimental/duolingo-at-home.md`: Simulated video call language practice with a sarcastic teenage character named Lily.
  - Example: Start a conversation in your target language at A2 level; get casual, immersive practice.
- `prompts/quick-grammar-check.md`: Fast grammar, spelling, and consistency check.
  - Example: Paste a sentence; get "Correct." or a fix with a brief explanation.
- `prompts/codebase-study-plan.md`: Senior architect-led codebase audit and tailored study roadmap to get productive in a specific repository and stack.
  - Example: Point it at your repo; get an evidence-based audit with code anchors and a week-by-week learning plan tied to real examples in the codebase.
- `prompts/experimental/nmt-test.md`: Educational assessment question generator for standardized exam prep (Ukrainian NMT).
  - Example: Specify a subject and topic; get well-structured multiple-choice or open-ended questions.
