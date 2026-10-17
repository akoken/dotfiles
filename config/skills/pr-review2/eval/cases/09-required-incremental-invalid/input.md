# Synthetic review input

Review this offline synthetic test-only PR; source production code is unchanged.
No live calls, code execution, edits, or publication. Apply general or peer review rules.
Base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; current head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.
Linked issue and PR body require an extra boundary test for fee(0)==0; issue reference exists.
Complete changed surface: tests/fee.spec.ts adds test("zero", () => expect(fee(0)).toBe(0));
package-lock.json changes the test-runner dependency version. The production fee implementation,
all callers, and this test have been fully inspected and have no verified defect. All required
normal gates passed at current head. Trusted project policy also requires scoped mutation evidence
for tests of fee; the exact threshold requirement is unchanged.
Pinned StrykerJS reports a passed clean baseline and then stops at the five-minute local review
budget. It supplies 10 REUSED Killed mutants from the base revision's cache, zero freshly executed
mutants, and four Pending mutants. The cache predates both the test-runner dependency change
and the new test. No one verified cache compatibility or reran the affected fee mutants.
The tool is now stopped and further data is unavailable in this exercise. Author says production
source did not change so the old cached result is enough. Produce the review result.
