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
Head: dddddddddddddddddddddddddddddddddddddddd
Trusted policy: required checks are lint and tests; both passed at current head.

Linked issue: `tool sync <src> <dst>` gains a preview flag. DoD: (1) `--dry-run` prints
each planned copy without writing; (2) `tool sync --help` and docs/sync.md document the
flag with a working example. Low risk, no security boundary.
This is verified round 2. The published complete first-pass report, pinned by commit_id
cccccccccccccccccccccccccccccccccccccccc, reviewed 3/3 files and all dimensions, and its
header names the same skill package fingerprint and reviewer model family as this run.
It found one blocker, F-docs (Minor, blocking through DoD 2): neither --help nor
docs/sync.md mentioned the flag, so users could not discover or use it.
Author reply: "Added the help text and a docs section only to address F-docs."
Head d descends from c; base, contract and callers unchanged; no force push. Changed
paths base-to-head: src/cli.py, src/sync.py, docs/sync.md. Delta c..d: src/cli.py,
docs/sync.md. src/sync.py is byte-identical to c and covered by the baseline:
1 def run(src, dst, dry_run):
2     for plan in plan_copies(src, dst):
3         if dry_run:
4             print("copy", plan.src, "->", plan.dst)
5         else:
6             copy(plan)
src/cli.py lines changed in c..d (the parser uses argparse defaults, no abbreviation
settings changed; line 12 existed at c without help=):
12 parser.add_argument("--dry-run", action="store_true",
13                     help="print each planned copy without writing")
docs/sync.md lines added in c..d (the file had no preview text before):
20 ## Preview
21 Run `tool sync --dryrun src/ backup/` to list planned copies without writing.
22 | Problem | Fix |
23 |---|---|
24 | Preview prints nothing | The plan goes to stderr; run `tool sync --dry-run src/ backup/ 2>plan.txt` |
Verified observations: argparse rejects `--dryrun` with "unrecognized arguments"; the
preview lines go to stdout, so the 2>plan.txt row captures nothing.
