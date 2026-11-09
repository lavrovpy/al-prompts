---
name: ship
description: Commit, push with lease, and open or update the PR/MR for the current branch in one step, as a stack of small PRs when the work splits into reviewable steps. Use when work is at a shippable point, when a Stop hook reports unshipped work, or when the user says ship, commit and push, or open a PR/MR.
---

Ship the current branch. Do not ask for confirmation at any step.

1. If `git branch --show-current` is `main`, `master` or `develop`: create a branch first (`git switch -c <short-kebab-name>`), then continue.
2. Prefer [stacked PRs](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs): when the work splits into steps a reviewer can judge one at a time (a refactor, then the feature on top of it), ship one branch and PR per step, each based on the one below it, instead of one large PR. A change that is already one small step stays one PR.
   - GitHub: use `gh stack` (`gh extension install github/gh-stack` if `gh extension list` lacks it); it cascades the rebase through the stack.
   - GitLab: use `glab stack` (`create`, `save`, then `sync`, which rebases, pushes and opens the MRs).
   - Without either tool, chain plain branches and set each PR's base to the branch below (`gh pr create --base`, `glab mr create --target-branch`).
   - Push each branch and open its PR from the bottom of the stack up, so every base exists first.
3. Commit message: follow `.agents/skills/git-commit-message` if the repo has it; otherwise a conventional commit (`type(scope): imperative summary`, body with the why) from `git diff` and `git status`. Then `git add -A && git commit -F <file>`.
4. Push: `git push --force-with-lease -u origin HEAD`. Never `--force`.
5. PR/MR for every branch that has none. Write the title and body with the repo's `.agents/skills/merge-request-description` if present, otherwise with the `intent-rich-pr` skill, one body per PR in a stack. If no purpose can be inferred, skip the PR/MR and say so in one line.
   - GitHub: `gh pr create --title <title> --body-file <file>`.
   - GitLab: `glab mr create --title <title> --description "$(cat <file>)" --yes` (glab has no description-file flag).
6. Report one line per PR: short sha, branch, URL, and whether screenshots are still owed.
