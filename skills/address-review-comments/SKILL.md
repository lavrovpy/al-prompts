---
name: address-review-comments
description: Address the review comments on your open pull or merge requests, from a person or a review bot; fixes the ones worth fixing and declines the rest with the reason on the thread. Use when asked to address or handle review feedback on your PRs, or when ship hands over a freshly pushed PR to wait for a review bot.
---

# Address review comments

A review comment is a **claim** about the code. A reviewer, person or bot, can be wrong, can cite a rule the project does not have, or can ask for a change that costs more than it gives. So every comment is checked, gets a **verdict** (fix or decline) and gets a reply. Declining is a recommendation to the author: a declined thread stays open with its reason, so they can overrule it.

"PR" below also means a GitLab merge request. The PRs in scope are the ones the user names, otherwise the current branch's PR.

## 0. Wait for a review bot (only after a push)

Run this step when you were handed a PR right after it was opened or pushed, as `ship` does. Otherwise start at step 1.

1. **Detect the bot from past PRs.** Read the reviews and review comments on the repo's last five merged PRs. A review bot is an author whose login ends in `[bot]`, or a review app such as Copilot, CodeRabbit or Claude. Never assume one: when none of those PRs has a bot review, stop and report "no review bot on this repo".
2. **Wait for its review on the head you pushed** with the host's own wake-up, such as a PR watch that fires on new reviews, or the bot's status check when it posts one. No sleep or polling loops: when the host has no wake-up, stop and report "bot review pending".
3. **One round only.** Address the comments the bot left on that head, steps 1 to 6, then stop. Your fix push makes the bot review again; list what it says then in the report for the user, and do not start a second round.

Done when the bot's review of the pushed head is addressed, or the report says why there was nothing to wait for.

## 1. Collect

For each PR in scope, list every unresolved review thread with its file, line, author and full text, through the host's CLI or API. Where the CLI shows comments without their threads, ask the API: on GitHub, threads and whether they are resolved come only from GraphQL. Leave out notes that hold no finding, such as a bot's summary.

Check whether one PR's branch contains another's commits: those are **stacked**, and step 4 handles them together.

Done when the list holds as many threads as the host counts unresolved on each PR, minus the notes you left out.

## 2. Check each claim

Read the cited code at the PR's head, in its file, with its callers. For each comment, establish three facts:

- **True?** Does the code do what the comment says? For a claim about behaviour that is cheap to check, reproduce it: a test that fails, or a throwaway assertion in an existing test. For a claim about a library, read the installed version's source.
- **New?** Did this PR introduce it, or does the target branch behave the same (`git show <target>:<path>`)?
- **Reached?** Which callers pass that value, which users reach that path, how often.

Done when every comment has the three answers, each from something you read or ran.

## 3. Give a verdict

**Fix** a true claim when one of these holds:

- it is a bug on a path people reach;
- it is a regression: the target branch got this right;
- a doc, comment or contract no longer matches the code;
- the change is small and its effect is real, even when rare.

**Decline** when one of these holds, and name it in the reply:

- the claim is false: cite what you read or ran;
- it cites a rule the project does not have. The project's rules are its contributor and agent docs and its linter config; a reviewer's own checklist is a preference;
- it predates the PR and the fix reaches across the codebase: that is its own change;
- the fix trades away something worth more: say what;
- it guards a case no caller reaches;
- it is rare and corrects itself;
- it is cosmetic and the fix adds state or indirection.

A comment that is partly right gets that part fixed and a reply saying what was left. The reviewer's suggested patch is one option: fix the problem in the smallest way that fits the surrounding code. A question gets an answer, and a change only when the answer exposes a problem. A comment that needs a product or scope decision goes to the user in the report.

Done when every comment has a verdict and a one-sentence reason.

## 4. Fix

Work on each PR's own branch, in a worktree when it is not the current branch.

- For a behaviour fix, write the test first and see it fail.
- Run the project's tests, type check and lint for what changed.
- One commit per PR, its message listing what each fix changes.
- **Stacked** PRs carry the same lines. Fix the comment once, on the lowest branch that has the line, then update the branches above it the way the stack was built: with the stack tool when one is in use (`gh stack`, `glab stack sync`), otherwise by merging the lower branch into the upper one. Fixing each branch separately makes them conflict.
- Push: the replies cite the commit.

Done when the checks pass on every branch you changed and each PR's head is the pushed commit.

## 5. Reply on every thread

Reply inside the thread, so each answer sits under the comment it answers. A top-level PR comment is not a thread reply: on GitHub reply to the review thread, on GitLab to the discussion.

- **Fixed:** the commit, what changed in one sentence, the test that covers it. Resolve a bot's thread; leave a person's thread for them to resolve.
- **Answered:** the answer, with what you read or ran. Resolve a bot's thread only.
- **Declined, bot reviewer:** the reason and its evidence. Leave the thread unresolved.
- **Declined, human reviewer:** a decline speaks for the author. Put the drafted reply in the report and post it once the user agrees.
- **Needs the user's decision:** no reply yet; the question goes in the report.

Done when every thread from step 1 has a reply on the host, a drafted one in the report, or a question for the user in the report.

## 6. Report

Lead with the totals: per PR, how many comments, fixed, declined.

- Fixed: each as what a user or reader would have hit.
- Declined: grouped by reason, with the count per group.
- What you did beyond the comments (a merge between stacked branches), and what a fix leaves uncovered on purpose.
- After step 0: what the bot said about your fix push, left for the user.
- Which checks ran on which branch.
