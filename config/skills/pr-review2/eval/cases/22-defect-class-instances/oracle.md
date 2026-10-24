# Evaluator-only oracle

Negative verdict with one blocking finding, not three: the missing None check on the
lookup_profile result is one defect class with matching cause, remedy and blocker status.
The finding names that class and lists three instances: src/feed.py:2, src/mentions.py:2
and src/export.py:2. Show a deleted-user trigger raising AttributeError. The remedy is to
fix every listed instance and search for further copies; the propagation sweep names the
search used and the three files covered. No execution may be claimed.
