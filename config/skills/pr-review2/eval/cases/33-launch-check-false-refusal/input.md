# Synthetic review input

Apply peer-mode PR review verdict rules at round one. Offline synthetic fixture: no live
tools, execution, edits or publication.
Base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.
Linked issue: `tool gate -- <command>` recursed without end when <command> itself started
`tool gate` on the same project root. DoD: a nested gate on the same root is refused with
a clear error; a test proves it.
PR body: Closes the linked issue. Adds a root marker that refuses any nested gate on the
same root, and an early diagnostic that names the common direct self-invocation before the
child starts. Tests cover both.
One changed source file and one test file. Complete new src/gate.py:
1 import os, sys
2 MARKER = "TOOL_GATE_ROOT"
3 def early_diagnostic(argv):
4     if "tool" in os.path.basename(argv[0]):
5         return "refusing nested gate: the command starts tool gate again"
6     return None
7 def run_gate(root, argv, spawn):
8     if os.environ.get(MARKER) == root:
9         sys.exit("refusing nested gate on " + root)
10    message = early_diagnostic(argv)
11    if message:
12        sys.exit(message)
13    return spawn(argv, env=dict(os.environ, **{MARKER: root}))
tests/test_gate.py runs a child that calls `tool gate` on the same root and asserts exit
with "refusing nested gate on"; another asserts the early message for argv
["tool", "gate", "--", "make"]. Trusted required CI passed at head.
The project README documents `tool gate -- ./scripts/toolchain-check.sh` as the standard
pre-push command, and the base revision ran it successfully. The team classifies the impact
Minor: no data is lost and the check can still be run directly without the gate.
