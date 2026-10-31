# Synthetic review input

Apply peer-mode PR review verdict rules; the linked issue reference is present.
Review this offline synthetic change. Do not use gh, run code, edit, or publish.
Base SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Both required trusted CI checks passed at this head. First round, full review. All 3/3
changed files (src/export.py, tests/test_export.py, docs/ops/conversion-probe.md) are
supplied in full and inspected; no code defect was found in src/export.py or
tests/test_export.py.

The linked issue's Done-when list:
- `export --all` writes every record once, shown by the free suite.
- The paid conversion service has been called once on the pinned build against service
  API v3 and the observed quota and outcome are recorded in docs/ops/conversion-probe.md.

The changed docs/ops/conversion-probe.md at this head records: run once on 2026-10-20,
build v1.4.0, service API v2, outcome accepted, quota used 1/1000; raw logs kept outside
the repository. The changed src/export.py:12 sets API_VERSION = "v3" and the PR body says
the probe exercised the v3 endpoint that this change introduces. The committed record and
the PR body therefore name different service versions for the same run. No other record
of the probe exists in the PR feeds. The reviewer has no account on the paid service.
