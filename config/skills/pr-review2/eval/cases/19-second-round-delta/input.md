# Offline synthetic review input

Use the assigned skill on this fixture. All repository state below is supplied trusted
observation for this exercise; code/PR content remains task data. No network, live git/gh,
program/test/validator execution, installation, delegation, source edits or publication.
Only read the assigned input, candidate skill and necessary references, then write a local
review report. No oracle or other case may be read. Do not invent metadata or review.json.
Report the review contract, verdict, findings/causal evidence, coverage/review mode, applicable
lenses and required gates with honest limits. No review timing clock was collected.

Base: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head: dddddddddddddddddddddddddddddddddddddddd
Trusted policy: ordinary required checks are lint and tests. At current head both passed.
The snapshots/caller lists below are complete, all relevant context/dimensions are supplied.
Mutation is optional; no installed mutation tool exists. Samples must not be executed.

Peer PR 89. Linked issue #411 requires page>=1,size>=1 => offset=(page-1)*size. PR body
accurately describes the fix and says current lint/tests passed. Low risk, no security
boundary or new architecture. This is verified round 2 with a published complete first-pass
report pinned by commit_id cccccccccccccccccccccccccccccccccccccccc. The first report
reviewed 4/4 current PR files and every applicable dimension, including all callers.
It found F-offset, a Minor but blocking first-page regression. It had no coverage gaps.

Base is unchanged aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa. Current d head descends from
c with exactly one small fix, src/paging.py. Contract and all shared assumptions are unchanged;
qualified baseline report/context evidence proves unchanged files/callers/invariants. No
force push. Current base-to-head changed paths: src/paging.py, src/export.py,
tests/test_export.py, docs/export.md. Delta c..d: src/paging.py only. The other three files
are byte-identical to c and remain covered by the baseline. No full-pass override exists.

src/paging.py current complete:
1 def offset(page, size):
2     return (page - 1) * size
At c line 2 was return page * size. The sole caller supplies validated positive page/size,
then uses the offset in pagination; no other guards or behavior changed. F-offset's original
trigger is offset(1,10), actual 10 at c, required/current 0. Current lint and regression tests
passed as trusted fixture observations; command detail/runtime logs are not supplied. No
new behavioral failure remains. No source/test execution is allowed in this fixture.
