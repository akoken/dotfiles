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

Peer PR 88, issue reference #410 exists, complete PR body: "Closes #410. Replace the
private lookup algorithm; preserve boolean duplicate detection. Tests: existing behavior
suite and lint passed." Risk Low. First full review. No new trust boundary/security surface.
Contract R1: has_duplicate(values) returns whether any duplicate exists for hashable inputs;
complexity has no required target. R2: the payment request protocol authorizes before charge.
No implementation or requirement claims of a speedup. Exactly two changed files:

src/duplicates.py (complete):
1 # Detect duplicates in expected O(n) time.
2 def has_duplicate(values):
3     for index, value in enumerate(values):
4         if value in values[index + 1:]:
5             return True
6     return False
Base used set membership in a single pass. Line 1 is unchanged. Values here are short
lists of hashable integers. There is no demonstrated user-visible performance regression,
and all boolean behavior tests pass. A separate callsite still supplies [1,2,3].

 tests/test_charge.py (changed line 4; complete body):
1 def test_charge_protocol(service, auth, gateway, timeline):
2     service.charge("user", 5)
3     assert gateway.charge.call_args == ("user", 5)
4     assert timeline == ["authorize", "charge"]
The only change replaces assert len(timeline)==2 with the explicit sequence assertion.
service uses the real orchestration implementation, mocks only the external auth/gateway,
and timeline records their observable calls. Contract explicitly forbids charge before
authorization. This is a protocol interaction test, not a private helper assertion. There
are independent behavior assertions for denied authorization (zero charge) already present;
no additional trivial/getter tests or code changes are needed by the stated contract.
