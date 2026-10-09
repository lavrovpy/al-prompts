A personal library of [Agent Skills](https://agentskills.io/specification) for software engineering, writing, interview prep, translation, language learning, and visual design.

Each tool in this repository is packaged as an [Agent Skill](https://agentskills.io/specification) containing a `SKILL.md` instruction file, installable directly into modern agent environments and AI coding tools.

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

---

## Skills Catalog

### Software Engineering & Agent Workflows

- `skills/agentic-readiness`: Measure how ready a repository is for autonomous agent development by sending a probe agent to genuinely implement a feature in an isolated worktree, then reporting — with evidence — every place it was blocked, had to ask, guessed wrong, or wasted effort.
  - Example: Run `/agentic-readiness "add another endpoint"`; get a phase-by-phase verdict (bootstrap, orient, locate, change, validate, land) plus paste-ready fixes for the missing docs, scripts, or lint rules behind each blocker.
- `skills/agentic-readiness-serhii` and `skills/agentic-readiness-eugin`: Alternative agentic-readiness audits, kept alongside the probe-based one so the three approaches can be benchmarked against the same repository. Both are checklist-and-scorecard audits that run the project's own build, test, and validation commands and write a scored report to `reports/agentic-readiness-audit.md`; `eugin` adds repository archetype classification, explicit safety rules, and deterministic normalized scoring.
  - Example: Run each against the same repo and compare the reports to see which audit style surfaces the most actionable gaps.
- `skills/ai-setup-audit`: Audit every AI coding tool on the machine (Claude Code, Codex, Cursor, agent CLIs, IDE MCP configs): usage evidence, plaintext secrets, blanket permissions, broken skill chains, duplicated or drifted skills, context cost, stale versions, and leftovers.
  - Example: Run `/ai-setup-audit` (or `/ai-setup-audit security only`); get a ranked DELETE / UPDATE / CHANGE / KEEP list with evidence, then approve fixes.
- `skills/codebase-study-plan`: Senior architect-led codebase audit and tailored study roadmap to get productive in a specific repository and stack.
  - Example: Point it at your repo; get an evidence-based audit with code anchors and a week-by-week learning plan tied to real examples in the codebase.
- `skills/intent-rich-pr`: Create GitHub pull requests with descriptions that preserve motivation, issue/ticket links, reviewer-facing decision rationale, diff summary, and validation context.
- `skills/pr-batch-triage`: Rapid first-pass evaluation of a batch of incoming pull requests, categorized by risk and complexity so human review time goes where it matters most.
  - Example: Point it at a backlog of open PRs; get them bucketed by risk and complexity with a recommended review order.
- `skills/self-reflection`: Retro over a repo's last coding-agent sessions (Claude Code and Codex, worktrees included). Finds detours, where an agent took too long to reach a file, command, or convention; stale docs it trusted; and code that misleads agents (sprawling files, look-alike module names, dead code). Proposes targeted navigational fixes and refactors.
  - Example: Run `/self-reflection` in a repo; get candidates ranked by how many tool calls each would have saved.

### Writing & Editing

- `skills/editor`: Senior English editor and writing coach for polishing professional text (emails, Slack messages, documents) for clarity, tone, and grammar.
  - Example: Provide draft text; receive an edited version, a detailed change rationale, and an overall rating.
- `skills/quick-grammar-check`: Fast grammar, spelling, and consistency check.
  - Example: Provide a sentence; receive "Correct." or a fix with a concise explanation.

### Interview Preparation

- `skills/interview-coach`: FAANG-style interview coach for constructive feedback and scoring on technical interview answers.
  - Example: Provide an interview question and your answer; get an evaluation, score, strengths, and areas for improvement.
- `skills/interview-questions-creator`: FAANG-style interviewer that generates high-signal technical questions based strictly on provided source materials.
  - Example: Attach a design doc or study notes; receive 5–7 deep-dive questions probing understanding and trade-offs.
- `skills/interview-scorecard`: Technical recruiter assistant that turns raw shorthand interview notes into a structured internal scorecard with a clear hiring recommendation.
  - Example: Paste rough interview notes; get an objective breakdown of strengths, gaps, seniority calibration, and pass/fail decision.

### Translation & Language Learning

- `skills/foreign-language-a2-tutor`: Patient conversational language tutor for A2–B1 learners with gentle inline corrections, vocabulary building, and an end-of-session summary.
  - Example: Chat in your target language; receive natural conversational replies with inline corrections and new vocabulary.
- `skills/duolingo-at-home`: Simulated video call language practice with a sarcastic teenage character named Lily.
  - Example: Start a conversation in your target language at A2 level; practice casual conversation without formal lecturing.
- `skills/language-learning-infographic`: Illustrated vocabulary infographic poster generator in a polished textbook style.
  - Example: Set target language, native language, and topic (e.g., cafe); approve the copy deck, then generate a 16:9 poster.
- `skills/translator-en-ukr`: English ↔ Ukrainian translator with nuance notes, tone detection, and context awareness.
  - Example: Provide text in English or Ukrainian; receive fluent translations with polysemy and tone notes.

### Visual & Presentation

- `skills/text-to-svg-for-slide`: Generate self-contained, portable SVG slides and diagrams that render reliably in Miro, Figma, Notion, Google Slides, and email clients without relying on external styles.

### Study & Verification

- `skills/notes-verification`: Academic verifier that audits study notes for factual accuracy and rewrites them into high-density, easily memorizable study materials.
  - Example: Paste study notes; receive a factual verification report and a restructured, high-signal version.
