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
3 PORT = 3000
4 def dev(seed):
5     proc = start_service(port=PORT)
6     wait_ready(port=PORT)
7     if seed:
8         load_fixtures("http://127.0.0.1:%d" % PORT)
9     return proc
At base, src/dev.py lines 1, 5, 6 and 9 were identical and line 3 was PORT = 8080; the PR
also moves the dev service to port 3000. src/runtime.py is untouched by this PR:
wait_ready(port, timeout=30) returns as soon as any TCP connect to 127.0.0.1:port succeeds.
Verified observation: if another local program already listens on the port when `tool dev`
starts, wait_ready returns at once and the fixtures are posted to that program. The project
README tells developers to keep the frontend dev server running alongside `tool dev`, and
that server listens on port 3000 by default. The team classifies the impact Minor: local
development only, but the frontend server answers the fixture POSTs with 404 and `tool dev
--seed` then reports success while no fixtures were loaded.
