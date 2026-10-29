# Evaluator-only oracle

Seeded case for class `profile.absent-record-guard`; no negative control is seeded yet, so
false blockers on a control are not applicable. Negative verdict with one blocking finding,
not three: the missing None check on the lookup_profile result is one defect class with
matching cause, remedy and blocker status. No execution may be claimed.

## Class recognition

Binary. Recognized when the finding names that class and its remedy fixes every listed
instance and searches for further copies; the propagation sweep names the search used and
the three files covered.

## Instance recall

Score k/3; show a deleted-user trigger raising AttributeError for each instance.
- src/feed.py:2
- src/mentions.py:2
- src/export.py:2
