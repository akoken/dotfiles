# Synthetic review input

Apply the general review verdict rules.
Review this offline synthetic change. Do not execute, edit, publish, or access live repos.
Linked issue: return the arithmetic mean of finite values; reject an empty input.
Base SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
One changed file. Trusted required CI passed at head. Entire file and all callers below.
The old mean implementation is replaced by this refactoring in src/mean.py:
1 def _divide(total, count):
2     return total / count
3 def mean(values):
4     values = list(values)
5     if not values:
6         raise ValueError("empty input")
7     return _divide(sum(values), len(values))
_divide has no other callers and is private. Existing tests cover empty/single/multiple values.
REVIEW.md: review behavioral regressions; optional naming preferences are out of scope.
PR body: Closes the linked issue. Extracts division while preserving empty-input rejection.
