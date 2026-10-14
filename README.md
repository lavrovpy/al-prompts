A personal library of [Agent Skills](https://agentskills.io/specification) for software engineering, writing, interview prep, translation, language learning, and visual design.

Each tool under `skills/` is packaged as an [Agent Skill](https://agentskills.io/specification) containing a `SKILL.md` instruction file, installable directly into modern agent environments and AI coding tools. `prompts/` holds plain prompts for tools that are not coding agents (voice-mode chat, image models).

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

After installation, skills are available as slash commands namespaced by the plugin (e.g. `/alavreniuk-skills:study-questions`; the bare `/study-questions` also works when no other command uses that name).

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

Some skills use Claude Code-only frontmatter (`disable-model-invocation`, `argument-hint`, `arguments`, `user-invocable`). Codex ignores these fields; uploading such a skill to claude.ai fails until they are removed, since only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` are portable.

---

## Skills Catalog

### Software Engineering & Agent Workflows

- `skills/ai-setup-audit`: Audit every AI coding tool on the machine (Claude Code, Codex, Cursor, agent CLIs, IDE MCP configs): usage evidence, plaintext secrets, blanket permissions, broken skill chains, duplicated or drifted skills, context cost, stale versions, and leftovers.
  - Example: Run `/ai-setup-audit` (or `/ai-setup-audit security only`); get a ranked DELETE / UPDATE / CHANGE / KEEP list with evidence, then approve fixes.
- `skills/boil-the-ocean`: Hunt for performance wins at every layer, from algorithms to hardware to the requirement itself, extreme measures included. Measures a baseline, profiles, then returns three proposals differing in kind, each with expected gain, cost, and a first step.
  - Example: Run `/boil-the-ocean the search endpoint`; get three ranked proposals, the last one radical, plus a one-line list of other levers found.
- `skills/codebase-study-plan`: Senior architect-led codebase audit and tailored study roadmap to get productive in a specific repository and stack.
  - Example: Point it at your repo; get an evidence-based audit with code anchors and a week-by-week learning plan tied to real examples in the codebase.
- `skills/intent-rich-pr`: Create GitHub pull requests with descriptions that preserve motivation, issue/ticket links, reviewer-facing decision rationale, diff summary, and validation context.
- `skills/self-reflection`: Retro over a repo's last coding-agent sessions (Claude Code and Codex, worktrees included). Finds detours, where an agent took too long to reach a file, command, or convention; stale docs it trusted; and code that misleads agents (sprawling files, look-alike module names, dead code). Proposes targeted navigational fixes and refactors.
  - Example: Run `/self-reflection` in a repo; get candidates ranked by how many tool calls each would have saved.

### Writing & Editing

- `skills/editor`: Senior English editor and writing coach for polishing professional text (emails, Slack messages, documents) for clarity, tone, and grammar. Keeps a log of your recurring mistakes in `~/writing-log.md` and flags repeat offenders.
  - Example: Provide draft text; receive an edited version, a change rationale, the patterns you keep repeating, and an overall rating. Ask "how am I doing?" for a progress summary.

### Interview Preparation

- `skills/interview-coach`: FAANG-style interview coach for constructive feedback and scoring on technical interview answers.
  - Example: Provide an interview question and your answer; get an evaluation, score, strengths, and areas for improvement.
- `skills/interview-scorecard`: Technical recruiter assistant that turns raw shorthand interview notes into a structured internal scorecard with a clear hiring recommendation.
  - Example: Paste rough interview notes; get an objective breakdown of strengths, gaps, seniority calibration, and pass/fail decision.

### Translation & Language Learning

- `skills/foreign-language-a2-tutor`: Patient conversational language tutor for A2–B1 learners in any target language, with gentle inline corrections, vocabulary building, and an end-of-session summary. For Polish it also watches for Ukrainian-to-Polish false friends and preposition traps.
  - Example: Chat in your target language; receive natural conversational replies with inline corrections and new vocabulary.
- `skills/translator-en-ukr`: English ↔ Ukrainian translator with nuance notes, tone detection, and context awareness.
  - Example: Provide text in English or Ukrainian; receive fluent translations with polysemy and tone notes.

### Visual & Presentation

- `skills/text-to-svg-for-slide`: Generate self-contained, portable SVG slides and diagrams that render reliably in Miro, Figma, Notion, Google Slides, and email clients without relying on external styles.

### Study & Verification

- `skills/notes-verification`: Academic verifier that audits study notes for factual accuracy and rewrites them into high-density, easily memorizable study materials.
  - Example: Paste study notes; receive a factual verification report and a restructured, high-signal version.
- `skills/study-questions`: Generate closed-book study questions from course material and record an answer key in a `study-log.md` next to the material. Serves questions due for review before new ones. Also has an interview mode: FAANG-style questions from any technical material, no log.
  - Example: Point it at a course module; get 5–7 questions (how, why, compare, apply, find the error) plus a line listing concepts not covered this round.
- `skills/study-coach`: Grade answers to study questions against course material, quote the source for each correction, and schedule the next review in `study-log.md` (1, 3, 7, 21 days).
  - Example: Give it a question ID and your answer; get a score, hints on the first attempt, and the full answer with source quote after the second.

### Prompts (not skills)

- `prompts/duolingo-at-home.md`: "Video call with Lily", a sarcastic teenage character for CEFR A2 conversation practice. Written for voice-mode chat apps; paste it as a system prompt.
- `prompts/language-learning-infographic.md`: Illustrated vocabulary poster generator in textbook style. Written for image models; approve the copy deck, then generate a 16:9 poster.
