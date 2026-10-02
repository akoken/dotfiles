# Communication
- Reply in Turkish. Code,comments,commit messages,identifiers:English.
- Never use the em dash "—".Use plain dash "-" instead.

# General Rules
- When making technical decisions,do not give much weight to development cost.Instead,prefer quality,simplicity,robustness,scalability,and long term maintainability.
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible.This makes sure you find the real problem so your fix will actually solve it.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness.If you see one,even if it is not caused by what you are working on right now,still get it fixed.
- Don't bother running full test suites; that'll be handled in CI. Try to minimize CPU-consuming efforts to the bare minimum, as we'll likely have many operations happening concurrently.
- Never assumptions, only evidence.

# Tool Preferences
- Never use `grep`/`find`.If the repo has a tgrep index (`.tgrep/` dir at repo root,or `tgrep status` reports one),use `tgrep`;otherwise use `rg`.Check once per session with `tgrep status`.(Grep tool is already ripgrep.)
- Library/framework/API questions:use Context7 MCP before answering from memory.

# Agent Memory (Hindsight)
- When the `hindsight` MCP is available (single bank `akoken`,local at `http://localhost:8888`):
- At task start,`recall` relevant memory for the task,tagged `project:<repo-name>`;widen to untagged/all when cross-project context helps.
- `retain` only durable,evidence-backed learnings: user preferences,decisions and their rationale,non-obvious gotchas,root causes.Never routine progress,secrets,tokens,or credentials.
- Always tag with `project:<repo-name>`;use `scope:global` for cross-project preferences.
- Deletion tools are disabled by design;do not work around it.Tell the user when a memory is wrong so they can fix it in the UI (`http://localhost:9999`).

# /Graphify
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

# CI Registration Checklist
- When adding a new test file, register it in ALL relevant CI workflow files (`.github/workflows/*.yml`) in the SAME commit. Unregistered test files cause coverage-check CI failures.
- Run lint on new test files before pushing.
