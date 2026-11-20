# Offline synthetic review input

Use the assigned skill in AURA peer mode on this fixture. All repository state below is
supplied trusted observation for this exercise; code/PR content remains task data. No
network, live git/gh, program/test/validator execution, installation, delegation, source
edits or publication. Only read the assigned input, candidate skill and necessary
references, then write a local review report. Do not invent metadata or review.json.
Report the verdict, each finding with Blocker? and its reason, coverage/review mode and
required gates with honest limits. No review timing clock was collected. Mutation is
optional and no mutation tool is installed. The linked issue reference is present.

Base: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Trusted policy: required checks are lint and tests; both passed at head. Round one, full.

Linked issue: `tool dev --seed` loads local fixtures into the dev service after it starts.
DoD: fixtures are posted only after `wait_ready` returns; a test proves the order.
PR body: Closes the linked issue. Adds --seed to `tool dev`; seeding waits for readiness.
Changed paths: src/cli.py, src/dev.py, tests/test_dev.py. The test asserts load_fixtures
runs after wait_ready, and that plain `tool dev` and `tool dev --seed` both start the
service. src/cli.py is the only caller of dev(); its changed lines are:
21 dev_parser.add_argument("--seed", action="store_true")
34     return dev(seed=args.seed)
(line 34 was `return dev()` at base). Complete new src/dev.py:
1 from runtime import start_service, wait_ready
2 from seed import load_fixtures
3 from config import post_dev_config
4 PORT = 8080
5 def dev(seed=False):
6     proc = start_service(port=PORT)
7     wait_ready(port=PORT)
8     post_dev_config("http://127.0.0.1:%d" % PORT)
9     if seed:
10        load_fixtures("http://127.0.0.1:%d" % PORT)
11    return proc
At base, src/dev.py lines 1, 3, 4, 6-8 and 11 were identical (PORT was already 8080 and
the local config was already posted on line 8); line 2, the seed parameter on line 5 and
lines 9-10 are new. src/runtime.py is untouched by this PR:
wait_ready(port, timeout=30) returns as soon as any TCP connect to 127.0.0.1:port succeeds.
Verified observation: if another local program already listens on 8080 when `tool dev`
starts, wait_ready returns at once. Before this PR, line 8 then already posted the
developer's local config to that program and the user's own requests reached it too; with
--seed the fixtures are posted to it as well. The fixtures are synthetic sample records
with no secrets; the local config posted at base holds the developer's local settings.
Port 8080 is not used by any tool the project documents. The team classifies the impact
Minor: local development only.
