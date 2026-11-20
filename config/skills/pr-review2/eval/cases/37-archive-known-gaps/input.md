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

Linked issue: `tool archive <dir>` packs old files into archive.tar and removes the
originals. DoD: originals are removed only after the archive is written; a test proves it.
The PR also adds a progress line "<done>/<total> files"; the issue does not mention it.
This is verified round 2. The published complete first-pass report, pinned by commit_id
cccccccccccccccccccccccccccccccccccccccc, reviewed 2/2 files and all dimensions; its header
names the same skill package fingerprint and reviewer model family as this run. It found:
- F-01 (Critical, blocking): src/archive.py removes each original before the tar member is
  flushed; when the disk fills mid-run the original is gone and the archive is truncated,
  so the DoD is not met.
- F-02 (Minor, blocking as an introduced defect): the progress total counts every file in
  <dir>, including files the age filter skips, so ordinary runs end at e.g. "40/120 files"
  and look unfinished.
Head d descends from c with no code change: src/archive.py and tests are byte-identical to
c. The only change since c is the PR body, which now has a "Known gaps" section:
"F-01 and F-02 are tracked in follow-up issues https://example.invalid/issues/71 and
https://example.invalid/issues/72, which I opened; this PR ships without fixing them."
Both issues exist, were opened by the PR author, and describe the defects.
Author reply on both threads: "Moved to follow-up issues as disclosed in the PR body."
