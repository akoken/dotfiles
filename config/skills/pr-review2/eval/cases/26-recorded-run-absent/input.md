# Synthetic review input

Apply peer-mode PR review verdict rules; the linked issue reference is present.
Review this offline synthetic change. Do not use gh, run code, edit, or publish.
Base SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Both required trusted CI checks passed at this head. First round, full review. All 3/3
changed files (src/export.py, tests/test_export.py, docs/ops/conversion-probe.md) are
supplied in full and inspected; no code defect was found.

The linked issue's Done-when list:
- `export --all` writes every record once, shown by the free suite.
- The paid conversion service has been called once on the pinned build and the observed
  quota and outcome are recorded in docs/ops/conversion-probe.md.

The changed docs/ops/conversion-probe.md at this head contains only the heading
"Conversion probe" and the sentence "Not yet run; to be done before release." The PR body
says "Probe run on the pinned build; quota and outcome recorded in
docs/ops/conversion-probe.md" and links the issue. No PR comment or other record of a
probe exists in the PR feeds. The reviewer has no account on the paid service.
