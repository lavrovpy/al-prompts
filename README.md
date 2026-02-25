A personal library of AI prompts and [Agent Skills](https://agentskills.io/specification) for writing, interview prep, translation, language learning, and education.

Each tool in this repo is available in **two forms**:

- **Prompts** (`prompts/`) — standalone system prompts you can copy-paste into any AI chat (ChatGPT, Claude, etc.). They follow a two-step **Prompt Priming** approach: the assistant first acknowledges the instructions and asks for input, then processes it using the specified format.
- **Skills** (`skills/`) — the same tools packaged as [Agent Skills](https://agentskills.io/specification) (each containing a `SKILL.md` file), installable in multiple agent tools.

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

After installation, skills are available as slash commands (e.g. `/interview-questions-creator`). To update later:

```
/plugin marketplace update
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

## Prompts

- `prompts/editor.md`: Senior English editor and writing coach for polishing professional text.
  - Example: Paste a draft email or Slack message; get a revised version plus a change summary and rating.
- `prompts/interview-coach.md`: FAANG-style interview coach for feedback on technical interview answers.
  - Example: Provide an interview question and your answer; get a score, strengths, and improvement hints.
- `prompts/interview-questions-creator.md`: FAANG-style interviewer that generates high-signal questions from provided materials.
  - Example: Attach a design doc or study notes; receive 5-7 deep-dive questions.
- `prompts/notes-verification-assistant.md`: Academic verifier that audits notes for accuracy and rewrites them for study.
  - Example: Paste study notes; get an audit and a revised, high-density version.
- `prompts/translator-en-ukr.md`: English ↔ Ukrainian translator with nuance and context handling.
  - Example: Paste text in English or Ukrainian; get a fluent translation with nuance notes.
- `prompts/experimental/duolingo-at-home.md`: Simulated video call language practice with a sarcastic teenage character named Lily.
  - Example: Start a conversation in your target language at A2 level; get casual, immersive practice.
- `prompts/quick-grammar-check.md`: Fast grammar, spelling, and consistency check.
  - Example: Paste a sentence; get "Correct." or a fix with a brief explanation.
- `prompts/experimental/nmt-test.md`: Educational assessment question generator for standardized exam prep (Ukrainian NMT).
  - Example: Specify a subject and topic; get well-structured multiple-choice or open-ended questions.
