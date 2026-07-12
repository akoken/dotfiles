---
name: testing-playwright-blazor
description: Test Blazor Server or WebAssembly applications with Playwright, including navigation, authentication, stable selectors, forms, SignalR updates, error UI, screenshots, HTTPS, parallelism, and CI. Use when creating or repairing Blazor browser tests or end-to-end test infrastructure.
---

# Playwright Testing for Blazor

## Workflow

1. Identify Blazor hosting mode, authentication flow, test framework, application startup command, base URL, HTTPS behavior, and existing Playwright fixtures.
2. Reproduce the user-visible behavior with stable semantic or explicit test selectors.
3. Wait for observable UI state; do not use arbitrary sleeps to compensate for rendering or SignalR timing.
4. Exercise the real navigation mode: full page load, enhanced navigation, or in-app routing.
5. Assert both the intended result and the absence of the Blazor error UI.
6. Capture bounded diagnostics on failure and dispose browser/application resources.
7. Run the focused test, then the repository's normal UI-test command.

Completion requires deterministic selectors and waits, coverage of the relevant loading/error state, and a passing test in the same hosting mode used by the application.

## Reference Routing

Read only the needed section in [references/full-guide.md](references/full-guide.md):

- setup and packages;
- navigation and wait strategies;
- selectors;
- authentication;
- click/touch and forms;
- Blazor error UI;
- SignalR updates;
- screenshots and visual testing;
- HTTPS, CI, parallelism, or debugging.

Use `rg -n '^## Pattern|^## CI/CD|^## Debugging|^## Advanced' references/full-guide.md` to locate the branch.

## Guardrails

- Prefer role, label, text, or explicit `data-testid` selectors over generated DOM structure.
- Never use `WaitForTimeout` as the primary synchronization mechanism.
- Keep credentials and real identity-provider dependencies out of ordinary browser tests.
- Make test data and accounts safe for parallel execution.
- Treat visible `#blazor-error-ui` as a failed test even when the final element appears.
