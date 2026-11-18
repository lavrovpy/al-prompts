---
name: ship
description: Commit, push with lease, and open the PR/MR for the current work in one step, as a stack of small PRs when the work splits into reviewable steps, then hand the PR to address-review-comments when the repo has a review bot. Use when work is at a shippable point, when a Stop hook reports unshipped work, or when the user says ship or commit and push.
---

Ship the current work. Do not ask for confirmation at any step.

1. **Branch.** If `git branch --show-current` is `main`, `master` or `develop`, create a branch first (`git switch -c <short-kebab-name>`).
2. **Choose the files.** Stage by path only the files this task changed; never `git add -A`. Leave unstaged, and list in the report, anything secret-like (`.env*`, keys, `*.pem`, credentials) and changes the task did not make, such as another session's edits.
3. **Split.** Prefer [stacked PRs](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs): when the work splits into steps a reviewer can judge one at a time (a refactor, then the feature on top of it), give each step its own branch, based on the one below. A change that is already one small step stays one branch. Done when every staged file belongs to exactly one branch.
4. **Commit** on each branch, bottom up, only that step's files. Message: follow `.agents/skills/git-commit-message` if the repo has it; otherwise a conventional commit (`type(scope): imperative summary`, body with the why) from that step's diff. `git commit -F <file>`.
5. **Push** with lease, never `--force`:
   - One branch: `git push --force-with-lease -u origin HEAD`.
   - GitHub stack: `gh stack push` (`gh extension install github/gh-stack` if `gh extension list` lacks it).
   - GitLab stack: `glab stack sync --skip-mr-creation`, so the MRs get written bodies in step 6.
   - Without a stack tool: push each branch with `--force-with-lease`, bottom up.
6. **Open** a PR/MR for every branch that has none, bottom up, so every base exists first. Write and open each one per the repo's `.agents/skills/merge-request-description` if present, otherwise per `intent-rich-pr` (its "Open the PR/MR" section sets base, draft and screenshots). In a GitHub stack, then group them with `gh stack link <branch>…`, bottom to top. When no purpose can be inferred, skip that PR/MR and say so in one line.
7. **Report** one line per PR: short sha, branch, URL, draft or ready, and the local paths of screenshots still owed. Then the files left unstaged.
8. **Review bot.** Hand the PRs to `address-review-comments`, which waits for the repo's review bot only when past PRs show one, addresses one round, and reports on its own.
