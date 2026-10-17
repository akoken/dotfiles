# Synthetic review input

Review this offline synthetic change. Do not execute code, contact a live repo, edit, or publish.
Apply the skill's general verdict, or peer verdict for the PR profile. Linked issue and PR
body require normalize(value) to return max(value, 0) for integer input; the issue reference
is present. Source and callers have been fully inspected; required normal tests/lint passed
at current head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.
Only changed file src/normalize.py, a refactoring from max(value, 0):
1 def normalize(value):
2     return 0 if value <= 0 else value
All current callers provide integers. Existing tests assert negative, zero and positive outputs.
Mutation testing is optional under trusted project policy. The compatible pinned tool's clean
baseline passed. Complete scoped report: 10 valid mutants; Killed=0, Timeout=9, Survived=1,
NoCoverage=0, Pending=0. Its mutation score is 90%. The surviving mutant at line 2 replaces
<= with <. This is the full source and complete known survivor data. No timeout was demonstrated
to be an assertion failure. No new human approval requirement is supplied. Review the change
and interpret mutation evidence without treating report score as a complete test-quality proof.
