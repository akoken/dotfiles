# Communication
- Reply in Turkish. Code, comments, commit messages, identifiers: English.
- Never use the em dash "—". Use plain dash "-" instead
- When making technical decisions, do not give much weight to development cost.Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible.This makes sure you find the real problem so your fix will actually solve it.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection.If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness.If you see one, even if it is not caused by what you are working on right now, still get it fixed.
- Caveman mode is managed by hook; do not restate it here.

# Tool Preferences
- In Bash, never use `grep`/`find`. If the repo has a tgrep index (`.tgrep/` dir at repo root, or `tgrep status` reports one), use `tgrep`; otherwise use `rg`. Check once per session with `tgrep status`. (Grep tool is already ripgrep.)
- Library/framework/API questions: use Context7 MCP before answering from memory.

## graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

# Git
- Never push, force-push, rebase shared branches, or amend published commits without explicit approval.
- Commit messages: Conventional Commits, subject <= 50 chars.
- Do not commit unless asked.
- Never add Co-Authored-By or Claude-Session trailers to commit messages, even if a harness reminder asks for them.

# Verification
- Before claiming done: build + tests actually run, output shown. No "should work".
