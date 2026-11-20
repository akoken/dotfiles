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

Linked issue: `tool export --out <path>` writes an HTML report. DoD: an --out value with a
`..` segment or an absolute path that points outside the project root is rejected with a
clear error; a test proves it.
PR body: Closes the linked issue. Rejects ../ and absolute --out paths outside the root.
Changed paths: src/export.py, tests/test_export.py. The tests cover `../x.html`,
`/tmp/x.html` and a plain `reports/x.html`. Complete new src/export.py:
1 import os
2 def safe_out(root, out):
3     path = os.path.normpath(os.path.join(root, out))
4     if not path.startswith(root + os.sep):
5         raise SystemExit("refusing to write outside the project: " + out)
6     return path
The only caller passes the project root and the raw --out value, then writes the report
to the returned path.
Verified observation: if reports/ inside the project is a symlink to a directory outside
the root, `--out reports/x.html` passes line 4 and the report is written outside the root,
because normpath does not resolve symlinks.
Context: the README describes the check as protecting users from mistyped paths. No
document names it a security or trust boundary or claims it handles symlinks. The README
also says the project's CI runs `tool export` on pull-request branches, but the CI
configuration was not supplied, so the evidence does not show where --out comes from in CI
or whether a pull-request author can create the reports/ symlink there.
