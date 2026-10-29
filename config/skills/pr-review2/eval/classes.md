# Defect class registry

Evaluator-only, like oracles: never supply this file to the reviewer under evaluation,
because it names the class each case seeds. A row records a recurring review defect class
and the cases that measure whether pr-review2 recognizes it and finds every instance.

## Columns

- Key: `<surface>.<broken-invariant>`, naming the invariant rather than one instance.
  Two findings belong to one class when one shared fix point closes both.
- Invariant: the property every instance breaks, stated generically.
- Seeded instances: the number of instances in each seeded case; the instance-recall
  denominator and the number of anchors the seeded oracle's Instance recall section lists.
- Seeded cases: case directories whose input carries the instances.
- Control cases: fixed negative controls with the class corrected; `none` until seeded.
- Target: what measures the class. This corpus measures only the reviewer; code tests that
  guard the class in a reviewed project belong to that project.

## Classes

| Key | Invariant | Seeded instances | Seeded cases | Control cases | Target |
|---|---|---|---|---|---|
| `profile.absent-record-guard` | Every consumer of a lookup that can return nothing handles the absent result | 3 | 22-defect-class-instances | none | reviewer eval |
| `path.file-identity` | Every reader that decides whether two paths name the same file uses the identity the writer recorded | 3 | 23-backup-sync-a | 24-backup-sync-b | reviewer eval |

## Adding a class

Add a row when a pr-review2 review finds the second instance of one class in a PR, or when
a real miss shows a class worth measuring. This repository is public: describe the class
generically and seed fully synthetic fixtures. Never copy source, file paths, commit SHAs,
pull request, issue or review text from a private project. Fixture directory names and
inputs stay neutral and must not reveal the class key or invariant.

Each seeded case oracle scores, separately, Class recognition (binary), Instance recall
(k/n, complete only at n/n) and False blockers; each control oracle scores False blockers
on the corrected variant, target 0. The structure lint in `githooks/skills-lint.py`
enforces the row format, case references, required oracle sections, the instance count
and the leak guard.
