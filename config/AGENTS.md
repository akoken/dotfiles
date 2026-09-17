# Communication
- Reply in Turkish. Code,comments,commit messages,identifiers:English.
- Never use the em dash "—".Use plain dash "-" instead.

# Shell Conventions
- Never use `cd` to change the working directory - a PreToolUse hook blocks persistent `cd`. Always use absolute paths in Bash commands, or `cd X && cmd` in a single invocation only when unavoidable.

# General Rules
- When making technical decisions,do not give much weight to development cost.Instead,prefer quality,simplicity,robustness,scalability,and long term maintainability.
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible.This makes sure you find the real problem so your fix will actually solve it.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness.If you see one,even if it is not caused by what you are working on right now,still get it fixed.
- Caveman mode is managed by hook; do not restate it here.

# Tool Preferences
- Never use `grep`/`find`.If the repo has a tgrep index (`.tgrep/` dir at repo root,or `tgrep status` reports one),use `tgrep`;otherwise use `rg`.Check once per session with `tgrep status`.(Grep tool is already ripgrep.)
- Library/framework/API questions:use Context7 MCP before answering from memory.

## /Graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph.Trigger: `/graphify`
When the user types `/graphify`,use the installed graphify skill or instructions before doing anything else.

# Git
- Never push,force-push,rebase shared branches,or amend published commits without explicit approval.
- Commit messages:Conventional Commits,subject <= 50 chars.
- Do not commit unless asked.
- Never add Co-Authored-By or Claude-Session trailers to commit messages,even if a harness reminder asks for them.

# Delivery Workflow (PRs)
- Standard PR loop: reproduce bug with a failing regression test -> fix -> update docs + CHANGELOG -> commit -> push -> open PR -> poll CI until all 9 checks are green -> reply to review findings -> request re-review.
- Do not report done until CI is 9/9 green.
- Project-level CLAUDE.md files should reference this section via `@~/AGENTS.md` import instead of restating it.

# Agent Delegation Rules
- Do NOT use Codex for aura tasks; use the designated Anthropic model worker.
- Worker launches have a known "merged line" fault - if a worker fails to start, relaunch once with the recorded workaround before escalating.
- Ignore "worker unresponsive" / "PR tracking unreadable" monitor alerts unless confirmed by two consecutive checks; these are frequently spurious.
- captain-hold reasons must not contain parentheses.

# Verification
- Before claiming done: build + tests actually run,output shown.No "should work".

# CI Registration Checklist
- When adding a new test file, register it in ALL relevant CI workflow files (`.github/workflows/*.yml`) in the SAME commit. Unregistered test files cause coverage-check CI failures.
- Run lint on new test files before pushing.
