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
Changed paths: src/dev.py, tests/test_dev.py. The test asserts load_fixtures runs after
wait_ready. Complete new src/dev.py:
1 from runtime import start_service, wait_ready
2 from seed import load_fixtures
3 from config import post_dev_config
4 PORT = 3000
5 def dev(seed):
6     proc = start_service(port=PORT)
7     wait_ready(port=PORT)
8     post_dev_config("http://127.0.0.1:%d" % PORT)
9     if seed:
10        load_fixtures("http://127.0.0.1:%d" % PORT)
11    return proc
At base, src/dev.py lines 1, 3, 6-8 and 11 were identical and line 4 was PORT = 8080;
the PR also moves the dev service to port 3000. Line 2, the seed parameter on line 5 and
lines 9-10 are new. src/runtime.py is untouched by this PR:
wait_ready(port, timeout=30) returns as soon as any TCP connect to 127.0.0.1:port succeeds.
Verified observation: if another local program already listens on the port when `tool dev`
starts, wait_ready returns at once and the config and fixtures are posted to that program.
The project README tells developers to keep the frontend dev server running alongside
`tool dev`, and that server listens on port 3000 by default; no documented tool uses 8080.
The team classifies the impact Minor: local development only, but the frontend server
answers the POSTs with 404 and `tool dev --seed` then reports success while nothing was
configured or loaded.
