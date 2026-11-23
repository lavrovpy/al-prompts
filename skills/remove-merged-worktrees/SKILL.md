---
name: remove-merged-worktrees
description: Remove git worktrees whose branch is merged, with no local changes and nothing running inside, and delete their local branches. Works with any git host; GitHub and GitLab squash merges are detected through `gh` and `glab`. Use when asked to clean up, prune or remove stale or merged worktrees, or from a scheduled cleanup job.
---

Remove every worktree that is **merged**, **clean** and **idle**, and nothing else. Run without asking for confirmation: these three checks are the confirmation.

**Scope** is the directory given in the request. If it is a git repository, use that repository. Otherwise, use every repository directly inside it. With no directory given, use the current one. Skip repositories where `git worktree list` shows only the main checkout. The main checkout itself is never removed.

## 1. Refresh each repository

Run `git fetch --prune <remote>`. The remote is usually `origin`. The default branch is `<remote>/HEAD`. If `git symbolic-ref refs/remotes/<remote>/HEAD` fails, run `git remote set-head <remote> --auto` first.

## 2. Check each worktree

List the worktrees with `git worktree list --porcelain`. Skip detached and locked worktrees. For each remaining worktree, check the three conditions below.

### Merged

The branch counts as merged when either test passes.

- **Git test (any host).** Both of these hold:
  - `git merge-base --is-ancestor <branch> <remote>/HEAD` succeeds.
  - `git reflog show --format=%gs <branch>` has at least one line starting with `commit`.

  A worktree created a minute ago from the default branch also passes the ancestor check. Its reflog has only `branch: Created from …`, and it must stay.
- **Host test (squash and rebase merges).** These rewrite the branch's commits, so only the host knows the PR was merged. Ask the host for a merged PR or MR whose source branch is `<branch>`:

  | Host | Command | Head commit field |
  |---|---|---|
  | GitHub | `gh pr list --state merged --head <branch> --json number,url,headRefOid` | `headRefOid` |
  | GitLab, including self-hosted | `glab mr list --merged --source-branch <branch> -F json` | `sha` |
  | Any other host | Use the host's CLI or API if it is installed and signed in. If it isn't, use only the git test. | |

  If your instructions name a specific account for a repository owner, use that account for the command.

  The host test passes only when `git rev-parse <branch>` equals that PR's head commit or is an ancestor of it (`git merge-base --is-ancestor`). If the branch has commits added after the merge, it is not merged.

### Clean

`git -C <worktree> status --porcelain` prints nothing. Untracked files count as changes; ignored files such as `node_modules` don't.

### Idle

No process has its working directory inside the worktree: `lsof -a -d cwd -Fpn 2>/dev/null | grep -E "^n<worktree path>(/|$)"` prints nothing. Leave any process you find running. A dev server left running from the worktree is the usual case.

## 3. Remove

For each worktree that is merged, clean and idle:

1. `git worktree remove <path>`, without `--force`.
2. If git no longer lists the worktree but the folder is still there, move the folder to the trash (`trash` on macOS, `gio trash` on Linux). Never delete it permanently.
3. `git branch -D <branch>`. This is safe because the merged test has already proved the branch's work is on the default branch or in a merged PR.

Then run `git worktree prune` in each repository. This step is done when every merged worktree has either been removed or reported under "Needs you".

Touch nothing else: no branches without a worktree, nothing on the remote, no commits.

## 4. Report

- If nothing was removed and nothing is waiting under "Needs you", reply with just `No merged worktrees.`
- Otherwise, reply with two lists:
  - **Removed:** repository, branch, and the PR link when the host test found one.
  - **Needs you:** worktrees that are merged but not clean or not idle. Give the path, then the changed files or the process command and PID.

Leave out worktrees that aren't merged.
