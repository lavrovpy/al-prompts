---
name: agentic-readiness-serhii
description: Audits whether a repository is ready for agentic development by inspecting it and actually running its build, test, and validation commands, then writing a scored report to reports/agentic-readiness-audit.md. This is the "serhii" variant, one of several agentic-readiness prompts kept side by side for benchmarking — invoke it explicitly by name.
---

You are auditing whether this repository is ready for agentic development.

Your task is to inspect the repository and determine whether an AI coding agent can understand the project, navigate the codebase, implement changes in the right places, build the application, run tests, and validate results.

Do not implement features. Do not refactor code. Do not change production files.

Create the final report here:

`reports/agentic-readiness-audit.md`

If the `reports/` folder does not exist, create it.

## **Important rules**

Use evidence from the repository. Do not guess.

Prefer existing documented commands over invented commands.

You must try to run the relevant build, test, and validation commands.

If you decide not to run a command because it is unsafe, destructive, requires unavailable credentials, or is impossible in the current environment, explain why in the report. In that case, the category should receive 0 points unless it is genuinely not applicable to this repository.

If a command exists but fails, report it as failed. Do not hide failures.

If no command or documentation exists for a category, report it as missing.

Use these statuses:

* ✅ Pass  
* ⚠️ Partial  
* ❌ Fail  
* N/A Not applicable

## **What to check**

### **1\. Agentic files**

Check whether the repository contains shared agentic files such as:

* `AGENTS.md`  
* `CLAUDE.md`  
* Cursor rules  
* Copilot instructions  
* `.claude/`  
* skills  
* slash commands  
* hooks  
* reusable agent prompts or templates

### **2\. Development guidance**

Check whether the repository gives an agent enough information to understand how to work in the project.

Look for documentation or instructions that explain:

* what the project does  
* repository structure  
* main frontend/backend/service areas  
* where different types of changes usually belong  
* existing implementation patterns  
* coding conventions  
* how to avoid duplicating existing logic  
* how to validate completed work

This can be in agentic files, README files, documentation folders, skills, or project-specific guides.

### **3\. Build readiness**

Check whether the agent can build the project.

Find the documented or obvious build command.

Run it.

Report:

* command found  
* command executed  
* result  
* blocker, if any (e.g., missing documentation or ambiguous instructions)

If the build command cannot be found or cannot be run, this category fails.

### **4\. Unit test readiness**

Check whether the agent can run unit tests.

Find the documented or obvious unit test command.

Run it.

Report:

* command found  
* command executed  
* result  
* blocker, if any

If the unit test command cannot be found or cannot be run, this category fails.

### **5\. Functional or integration test readiness**

Check whether the agent can run functional, integration, API, service-level, or end-to-end backend tests.

Find the documented or obvious command.

Run it if the required local services can be started safely.

Report:

* command found  
* command executed  
* result  
* blocker, if any

If the command cannot be found or cannot be run, this category fails.

### **6\. API/runtime validation readiness**

Check whether the agent can validate the running application through API calls, curl commands, HTTP scripts, Postman/Newman, or another documented runtime validation method.

If the application can be started locally, try to validate at least one basic health check, endpoint, or documented API flow.

Report:

* runtime command found  
* validation method found  
* command or request executed  
* result  
* blocker, if any

If this is not possible, this category fails unless the repository is not an API/service application.

### **7\. Browser/UI validation readiness**

If the repository has a frontend UI, check whether the agent can validate it in a browser.

Look for:

* Playwright  
* Cypress  
* Selenium  
* browser MCP  
* documented browser test command  
* screenshot or test report generation

Run the documented browser/UI validation command if possible.

Report:

* browser validation tool found  
* command executed  
* result  
* artifacts produced, if any  
* blocker, if any

If the repository has a UI but no browser validation method exists or it cannot be run, this category fails.

If the repository has no UI, mark this category as N/A.

### **8\. Coverage readiness**

Check whether the agent can measure test coverage.

Find a documented or obvious coverage command.

Run it if possible.

Report:

* coverage command found  
* command executed  
* coverage result  
* coverage threshold, if one exists  
* blocker, if any

If no coverage command exists, mark this category as failed or partial depending on whether normal test commands still provide useful coverage information.

## **Report format**

Write the report using this structure:

# **Agentic Readiness Audit**

## **1\. Executive Summary**

* Overall status: Ready / Partially ready / Not ready  
* Readiness score: X / 100  
* Can an AI coding agent work in this repository today?: Yes / Partially / No  
* Main blockers:  
  * ...  
* Top recommendations:  
  * ...

## **2\. Scorecard**

Create a table with these columns:

* Category  
* Status  
* Score  
* Evidence  
* Recommendation

Use these categories and scores:

| Category | Max score |
| ----- | ----- |
| Agentic files | 10 |
| Development guidance | 15 |
| Build readiness | 15 |
| Unit test readiness | 15 |
| Functional/integration test readiness | 15 |
| API/runtime validation readiness | 10 |
| Browser/UI validation readiness | 10 |
| Coverage readiness | 10 |
| Total | 100 |

Scoring rules:

* Give full points only when the capability exists and works.  
* Give partial points only when the repository has useful guidance or commands, but something is incomplete.  
* Give 0 points when the command is missing, cannot be run, was skipped, or fails.  
* If a category is genuinely not applicable, mark it N/A and explain why. Do not penalize backend-only repositories for missing browser tests.

## **3\. Findings**

For each category, briefly explain:

* what was found  
* what was missing  
* what was executed  
* what passed or failed  
* what should be improved

## **4\. Commands Executed**

Create a table with:

* Command  
* Purpose  
* Result  
* Notes

Include only commands you actually ran.

## **5\. Gaps and Recommendations**

Create a prioritized table with:

* Priority: High / Medium / Low  
* Gap  
* Why it matters  
* Recommended fix  
* Suggested file/path

## **6\. Final Recommendation**

State whether this repository is ready for:

* research tasks  
* testing tasks  
* implementation tasks  
* API/runtime validation  
* frontend/browser validation  
* autonomous Jira ticket execution

Also state what must be fixed before the repository can be considered agentic-ready.

## **Readiness interpretation**

Use this interpretation:

* **Ready**: The repository has useful agentic files or development guidance, and the agent can build the project, run relevant tests, and validate results.  
* **Partially ready**: The agent can understand the project, but some build, test, validation, or coverage capability is missing or blocked.  
* **Not ready**: The agent cannot reliably understand, build, test, or validate the project.

A repository should not be marked Ready if the agent cannot build the project or run the relevant tests.

## **Final output**

After creating the report, respond only with:

`Agentic readiness audit completed: reports/agentic-readiness-audit.md — Overall status: <status>`

