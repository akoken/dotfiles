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

First full general review. Medium risk, no credentials/tenant/untrusted execution boundary
changes. Contract R1: export must report upstream failure rather than silently claim an
empty successful export. R2: Balance instances must always be nonnegative, including after
set_balance. R3: the CLI owns final failure rendering; cancellation must reach that boundary.
Exactly four changed files below; all callers are included. No other files changed.

src/export.py (complete):
1 def export(client):
2     try:
3         rows = client.fetch_rows()
4     except ConnectionError:
5         rows = []
6     return {"ok": True, "rows": rows}
Base directly fetched rows; ConnectionError propagated. Current caller prints success when
ok is true. fetch_rows can raise ConnectionError on outage; it never returns cached rows.

src/balance.py (complete):
1 class Balance:
2     def __init__(self, amount):
3         if amount < 0:
4             raise ValueError("negative balance")
5         self.amount = amount
6     def set_balance(self, amount):
7         self.amount = amount
set_balance is newly added. A current trusted in-process adjustment caller can supply -1;
it relies on this type's nonnegative invariant and has no upstream guard. There is no
serialization or external security boundary change. The domain contract explicitly
requires rejecting negative mutations, not merely construction-time validation.

src/cli.py (complete):
1 def run(operation, ui):
2     try:
3         return operation()
4     except Exception as error:
5         ui.report_failure(error)
6         return 1
Change only adds line 5, previously absent. This is the documented outermost CLI boundary.
ui.report_failure emits a redacted failure and exit 1 is the required unsuccessful result.
All operation errors here are ordinary Exceptions; callers expect run to consume them.

src/worker.py (complete):
1 def read_next(source):
2     return source.read()
New extraction from existing call site. source.read may raise cancellation or ConnectionError;
the only caller is run(lambda: read_next(source), ui), the documented reporting boundary.
There is no requirement for local logging/catching in read_next. No fallback is performed.
