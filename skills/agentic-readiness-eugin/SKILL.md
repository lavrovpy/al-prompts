---
name: agentic-readiness-eugin
description: Audit whether this repository is ready for agentic development and write a scored report to reports/agentic-readiness-audit.md
agent: build
subtask: false
---

# Agentic Repository Readiness Audit

Audit whether this repository is ready for agentic development. Determine whether an AI coding agent can understand the project, set up its environment, navigate the codebase, locate the correct implementation areas, build or otherwise validate deliverables, check code quality, run relevant tests, and validate results.

Do not implement features or refactor code. This is an audit of repository readiness, not a contribution.

## Audit request

Optional user-provided scope, constraints, exclusions, or time budget:

```text
$ARGUMENTS
```

If no arguments are provided, audit the entire repository. For a monorepo, prefer root orchestration commands that cover all workspaces. If none exist, inspect each workspace. Do not silently sample. If full coverage is infeasible, identify every unaudited workspace, explain why it was omitted, and mark affected categories `⚠️ Partial`.

## Safety and workspace integrity

- Do not edit existing tracked files except the required audit report.
- Capture the initial commit, branch, and `git status --short` before running validation commands. Preserve all pre-existing changes and never revert or delete work you did not create.
- Use frozen or immutable dependency installation whenever the ecosystem supports it, such as `npm ci`, `pnpm install --frozen-lockfile`, `yarn --immutable`, or an equivalent documented command. Do not allow an install to rewrite a lockfile.
- Run formatters only in check/diff mode. Never run a formatting or lint-fix command that rewrites source files.
- Before executing a command, inspect it and any wrapper it invokes. Never run deployment, release, publish, production, destructive migration, teardown, cloud-mutating, privileged, or `sudo` commands.
- Do not use real secrets, production credentials, production endpoints, or live customer data. Do not transmit repository content or secrets to external services.
- Restrict runtime/API checks to local or explicitly documented disposable test environments. Use only test or dummy credentials.
- Prefer documented dry-run, check-only, local, sandbox, container, or disposable test modes.
- Use explicit command timeouts when supported. Unless repository documentation establishes a longer expected runtime, allow at most 15 minutes per command. Do not leave commands, servers, watchers, containers, or background processes running indefinitely.
- Track services, processes, containers, and disposable artifacts started by the audit. Stop only resources started by the audit. Remove an artifact only when it is unambiguously audit-created, disposable, and not a pre-existing user file.
- If a command is known to mutate tracked files or external state and no safe mode exists, do not run it. Record the exact safety reason.
- After validation, compare the final worktree state with the initial state. Do not automatically revert unexpected changes; report them and stop the affected validation path. The report itself is the only intended tracked-file change.

## Evidence and command selection

- Use evidence from the repository. Do not guess. Use `Unknown` when a fact cannot be established.
- Inspect and triangulate all relevant command sources:
  - CI/CD pipelines such as `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, and `azure-pipelines.yml`
  - Agent instructions such as `AGENTS.md`, `CLAUDE.md`, `.opencode/`, and `.claude/`
  - `README` files, `CONTRIBUTING.md`, and project documentation
  - Task runners and package scripts such as `Makefile`, `package.json`, `justfile`, `Taskfile.yml`, `tox.ini`, and `pyproject.toml`
  - Build and tool configuration files
- Treat CI as evidence of required gates, not automatically as a locally runnable command. Prefer a documented local wrapper that reproduces CI. Report contradictions or drift among CI, documentation, agent instructions, and task runners.
- Cite evidence with repository-relative file paths and line numbers when practical.
- Prefer documented commands over invented commands. A minimally adapted command is acceptable only when needed for a safe check-only, local, or non-interactive mode; show and explain the adaptation.
- Try to run every relevant and safe setup, build, static-validation, test, and runtime-validation command.
- Record the exact command, working directory, exit code, duration, timeout, result, and relevant artifacts. Do not report a command as passed solely because configuration for it exists.
- If no command or documentation exists, report it as missing.
- If a command exists but fails, report the failure. Do not hide or reinterpret it as a pass.

## Repository classification and applicability

Before scoring, classify the repository and justify the classification with evidence. It may have multiple archetypes:

- Application or service
- Frontend/UI application
- CLI tool
- Library or SDK
- Infrastructure as code or deployment configuration
- Documentation or content repository
- Data, model, or pipeline repository
- Monorepo containing multiple archetypes
- Other

Determine category applicability from the archetype rather than assuming every repository is an application. Use repository-native equivalents where appropriate, such as `terraform validate`, `tofu validate`, `helm lint`, documentation builds, link checks, schema validation, notebook checks, or package verification.

A category is `N/A` only when the capability genuinely has no relevant surface in the classified repository. Missing implementation, commands, documentation, tests, or credentials does not make a category N/A.

## Status and execution classifications

Category readiness status:

- `✅ Pass` — the capability is documented or discoverable, was safely executed where execution applies, and works across the audited scope
- `⚠️ Partial` — useful capability exists, but it is incomplete, only partly covers the scope, or could not be fully verified because of an auditor-environment limitation
- `❌ Fail` — repository capability is missing, unsafe by design, cannot be followed from repository guidance, or was executed and failed
- `N/A` — genuinely not applicable to the repository archetype

Also classify command execution separately:

- `Verified` — executed successfully
- `Failed` — executed and returned a failure, timed out, or produced invalid results
- `Blocked: repository` — repository-owned instructions, prerequisites, fixtures, safe credentials, or commands are missing or unsafe
- `Blocked: environment` — repository guidance is complete, but the auditor machine lacks an external prerequisite such as Docker, network access, a browser, or an installed tool
- `Not run: unsafe` — execution would violate the safety rules
- `Not applicable` — no relevant execution exists for this archetype

An environment-blocked category can receive at most `⚠️ Partial`; it must never receive `✅ Pass`. A repository-owned blocker is `❌ Fail`.

## Deterministic scoring

Use only these category scores:

- `✅ Pass` = 10 points
- `⚠️ Partial` = 5 points
- `❌ Fail` = 0 points
- `N/A` = excluded from the applicable maximum

Calculate and report both:

- `Raw score = awarded points / applicable maximum`
- `Normalized readiness score = round(awarded points / applicable maximum × 100)`

Apply readiness thresholds to the normalized score, not the raw points.

After classifying the repository, identify its mandatory validation gates. At minimum these are:

- Environment/dependency setup, when dependencies or a toolchain are required
- Build/package/render validation, when the repository produces a buildable, packageable, renderable, or deployable artifact
- At least one primary repository-native automated validation capability appropriate to the archetype, such as static validation, unit tests, integration tests, CLI smoke tests, infrastructure validation, documentation checks, or browser tests

Readiness interpretation, evaluated in this order:

1. `Not ready` — normalized score is below 50, or any applicable mandatory gate is `❌ Fail`.
2. `Ready` — normalized score is at least 80, every applicable mandatory gate is `✅ Pass`, and no repository-owned blocker prevents normal agent work.
3. `Partially ready` — every other result, including a score from 50 through 79 or a mandatory gate that is `⚠️ Partial` because verification was incomplete.

If no category is applicable, do not calculate a normalized score; report `Not ready` and explain that the repository could not be meaningfully audited.

## What to check

### 1. Agentic files and project-specific knowledge (10 pts)

Check for shared agent instructions and project-specific knowledge:

- `AGENTS.md`, `CLAUDE.md`, `.opencode/`, `.claude/`, Cursor rules, and `.github/copilot-instructions.md`
- Project-local skills, slash commands, hooks, reusable prompts, and templates
- Scope rules for nested instructions in a monorepo
- Whether instructions are specific enough to guide real changes and avoid common mistakes
- Whether instructions agree with current code, CI, and project structure

Use git history only as supporting context. Record a last-modified date when available, but do not call documentation stale solely because it is old.

### 2. Development guidance (10 pts)

Check whether an agent can determine:

- What the project does and its primary technologies
- Repository structure and major frontend, backend, service, package, infrastructure, or documentation areas
- Where different types of changes belong
- Existing implementation patterns, boundaries, generated files, and conventions
- How to find and reuse existing logic instead of duplicating it
- How to validate completed work
- Ownership or review guidance when present

Flag concrete contradictions between guidance and the repository.

### 3. Environment and dependency setup (10 pts)

Check whether an agent can reproduce the required environment from a clean state:

- Toolchain and version declarations such as `.nvmrc`, `.tool-versions`, runtime constraints, and package-manager versions
- Lockfiles and immutable dependency installation
- Container, Compose, devcontainer, Nix, or equivalent reproducible environments
- Environment-variable schemas or examples and documented test-safe values
- Required local services, fixtures, seed data, and secrets-management guidance

Run the documented safe setup command when possible. State whether setup was genuinely tested from a clean/disposable environment or only in an existing warmed workspace. A successful install in a warmed workspace does not prove clean-state reproducibility.

### 4. Build, package, or render readiness (10 pts)

Find and run the repository-native command that produces or verifies its deliverable, such as an application build, library package, documentation render, container build, or equivalent. If no build-like step is relevant, mark N/A and justify it from the repository archetype.

Report the command source, execution result, blocker, and produced artifacts.

### 5. Lint, format-check, typecheck, or static-validation readiness (10 pts)

Check the applicable quality gates, including linters, formatter check modes, type checkers, schema validators, IaC validators, documentation checks, and pre-commit or git-hook configuration.

Run safe check-only commands. If multiple tools exist, report their individual and aggregate results. Do not run fix or rewrite modes.

### 6. Unit, component, or repository-native test readiness (10 pts)

Find and run unit, component, package, module, infrastructure, documentation, or other repository-native isolated tests appropriate to the archetype. Report test selection, scope, result, and blocker.

Mark N/A only when the repository has no testable isolated behavior and another repository-native validation category covers its primary correctness surface.

### 7. Functional or integration test readiness (10 pts)

Find and safely run applicable integration, service-level, API, database, contract, system, or backend E2E tests. Start required local services only when they are documented, safe, and disposable.

Mark N/A only when the repository genuinely has no integration surface. Explain the reasoning.

### 8. Runtime, API, or CLI validation readiness (10 pts)

Check whether an agent can validate observable behavior through a local health check, API request, HTTP script, Postman/Newman collection, CLI smoke test, local preview, or another documented runtime method.

If safe, start the application locally and execute at least one representative validation. Do not contact production or an undocumented external service. Mark N/A only when the repository has no runtime, API, CLI, preview, or equivalent executable surface.

### 9. Browser or UI validation readiness (10 pts)

For repositories with a UI, check for Playwright, Cypress, Selenium, browser tooling, documented manual flows, screenshot generation, traces, and test reports. Run the documented safe browser/UI validation command when possible and record artifacts.

Mark N/A when the repository has no UI.

### 10. Coverage and validation-depth readiness (10 pts)

For repositories where coverage is meaningful, find and run the documented coverage command. Report the measured result, configured threshold, scope, and artifact path. Distinguish a configured enforceable threshold from informational coverage output.

Mark `⚠️ Partial` when useful coverage output exists but is not reproducible, comprehensive, or threshold-enforced. Mark N/A when code coverage is not meaningful for the repository archetype, and explain which validation-depth evidence was used instead.

Do not award multiple categories full credit from one command unless its output independently demonstrates each claimed capability. Explicitly identify commands reused as evidence across categories.

## Report output

Create the final report at:

```text
reports/agentic-readiness-audit.md
```

Create `reports/` if needed. Use exactly the following structure.

### Header

```markdown
# Agentic Readiness Audit

- Audited by: <agent name and model ID, or Unknown>
- Started: <ISO-8601 timestamp>
- Completed: <ISO-8601 timestamp>
- Commit SHA: <initial git rev-parse HEAD>
- Branch: <initial branch or detached HEAD>
- Initial worktree: <clean, or concise list of pre-existing changes>
- Final worktree: <clean except report, or concise list of changes>
- Platform: <OS and architecture>
- Repository archetype: <classification>
- Scope: <entire repository or explicit scope/workspaces>
- Clean-state setup verified: <Yes | No — warmed workspace only | Blocked, with reason>
- Audit constraints: <arguments, environment limitations, and time budget>
```

### 1. Executive Summary

- Overall status: `Ready` | `Partially ready` | `Not ready`
- Raw score: `X / Y applicable points`, or `N/A` when no category is applicable
- Normalized readiness score: `Z / 100`, or `N/A` when no category is applicable
- Can an AI coding agent work in this repository today?: `Yes` | `Partially` | `No`
- Mandatory validation gates: <gate and status list>
- Main blockers: ...
- Top recommendations: ...

### 2. Scorecard

Create a table with:

`Category | Applicability | Status | Score | Execution | Evidence | Recommendation`

| Category | Max |
| --- | --- |
| Agentic files and project knowledge | 10 |
| Development guidance | 10 |
| Environment and dependency setup | 10 |
| Build, package, or render readiness | 10 |
| Lint, format-check, typecheck, or static validation | 10 |
| Unit, component, or repository-native tests | 10 |
| Functional or integration tests | 10 |
| Runtime, API, or CLI validation | 10 |
| Browser or UI validation | 10 |
| Coverage and validation depth | 10 |

Show `10`, `5`, `0`, or `N/A` for each category. Show both the raw and normalized totals below the table.

### 3. Findings

For every category, state:

- What was found and where
- What was missing or contradictory
- What was executed, including working directory
- What passed, failed, or was blocked
- Scope and confidence of the evidence
- What should improve

### 4. Commands Executed

Create a table with:

`Command | Working directory | Purpose | Exit code | Duration | Execution status | Notes/artifacts`

Include only commands actually executed. Put inspected but unexecuted commands and the reason they were not run in the relevant finding.

### 5. Gaps and Recommendations

Create a prioritized table with:

`Priority (High/Medium/Low) | Gap | Why it matters | Recommended fix | Suggested file/path`

Prioritize repository-owned blockers over auditor-environment limitations.

### 6. Final Recommendation

State whether the audited scope is ready for:

- Research tasks
- Testing tasks
- Implementation tasks
- Runtime/API/CLI validation
- Frontend/browser validation
- Autonomous ticket execution

State what must be fixed before the repository can be considered agentic-ready and identify any unaudited scope.

## Final response

After writing the report, respond with exactly:

```text
Agentic readiness audit completed: reports/agentic-readiness-audit.md
Overall status: <Ready | Partially ready | Not ready> — Score: <normalized score>/100
Top blocker: <one line, or None>
```

If no category is applicable, use `Score: N/A` instead of the score expression above.
