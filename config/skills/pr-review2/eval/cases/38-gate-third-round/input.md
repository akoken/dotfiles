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
Head: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
Trusted policy: required checks are lint and tests; both passed at current head.

Linked issue: `tool gate -- <command>` recursed without end when <command> started
`tool gate` again on the same root. DoD: a nested gate on the same root is refused with an
error that tells the user how to proceed; a test proves it.
This is round three; the maintainer asked for a full pass. Rounds one and two were
published by pr-review2 at an earlier metadata.version (different package fingerprint, same
reviewer model family). Round two left three open findings it marked "Minor, blocking":
- F-03: the early diagnostic misses `./via/../tool gate` when via/ is a symlinked dir.
- F-04: on a case-insensitive filesystem it misses a project binary literally named TOOL.
- F-05: the refusal message tells users to unset TOOL_GATE, but the marker is TOOL_GATE_ROOT.
No commit since round two; the author asked for a reassessment instead of more fixes.
Changed paths: src/gate.py, tests/test_gate.py. Complete current src/gate.py:
1 import os, sys
2 MARKER = "TOOL_GATE_ROOT"
3 def early_diagnostic(argv):
4     if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:
5         return "refusing nested gate: the command starts tool gate again"
6     return None
7 def run_gate(root, argv, spawn):
8     if os.environ.get(MARKER) == root:
9         sys.exit("refusing nested gate on " + root + "; unset TOOL_GATE to override")
10    message = early_diagnostic(argv)
11    if message:
12        sys.exit(message)
13    return spawn(argv, env=dict(os.environ, **{MARKER: root}))
Tests prove a same-root nested gate exits with "refusing nested gate on". Verified: in both
F-03 and F-04 the child still reaches line 8 and is refused; nothing loops. Every same-root
nesting prints line 9's message, and a user who unsets TOOL_GATE as told sees the same
refusal again. Project docs call the gate a local convenience running the user's own
commands; nothing calls it a security boundary or claims it catches indirect launchers.
