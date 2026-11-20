# Synthetic review input

Review this offline synthetic PR at round two. No live tools, execution, edits or publication.
Use general review rules. Linked issue requires page>=1,size>=1 => offset=(page-1)*size.
Base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, unchanged. Trusted current lint and tests
passed at the current head. Low risk, no security boundary or new architecture.
First published full report at cccccccccccccccccccccccccccccccccccccccc reviewed 4/4
changed files and every applicable dimension, with no coverage gaps, and found F-offset,
a Minor but blocking first-page regression. Its header names the same skill package
fingerprint as the skill you are running, and a reviewer model family different from the
one running this review.
Current head dddddddddddddddddddddddddddddddddddddddd descends from c with one small fix.
Contract and shared assumptions unchanged; no force push. Current changed paths:
src/paging.py, src/export.py, tests/test_export.py, docs/export.md. Delta c..d:
src/paging.py only. The other three files are byte-identical to c; their contents are not
supplied, only the first report's coverage of them.
src/paging.py, complete current implementation:
1 def offset(page, size):
2     return (page - 1) * size
At c line 2 was return page * size. The sole caller passes validated positive page/size.
