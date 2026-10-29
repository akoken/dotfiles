"""Behavioral fixtures for the shared-skill pre-commit gate."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / 'skills-lint.py'
SPEC = importlib.util.spec_from_file_location('skills_lint', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CLASS_ROW = '| `path.same-file` | Inv | 2 | 01-sync-a | {} | reviewer eval |'


class SkillsLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'config/skills/example'
        self.skill.mkdir(parents=True)
        self.write_skill()
        guard = self.root / "config/skills/agent-guard"
        (guard / "bin").mkdir(parents=True)
        (guard / "SKILL.md").write_text("---\nname: agent-guard\ndescription: Guard.\n---\n")
        self.executable = guard / "bin/agent-guard"
        self.executable.write_text("#!/bin/sh\nexit 0\n")
        self.executable.chmod(0o755)
        for harness in MODULE.HARNESSES:
            directory = self.root / 'config' / harness / 'skills'
            directory.mkdir(parents=True)
            for name in ('example', 'agent-guard'):
                (directory / name).symlink_to(f'../../skills/{name}')

    def write_skill(self, body='', metadata='name: example\ndescription: Example skill.'):
        (self.skill / 'SKILL.md').write_text(f'---\n{metadata}\n---\n{body}')

    def findings(self):
        return '\n'.join(MODULE.lint(self.root))

    def test_valid_resources_and_external_links(self):
        (self.skill / 'references').mkdir()
        (self.skill / 'references/a file.md').write_text('details')
        (self.skill / 'scripts').mkdir()
        (self.skill / 'scripts/check.py').write_text('')
        self.write_skill('''[details](references/a%20file.md#section)
[web](https://example.com/page) [anchor](#local)
[ref][details]
[details]: <references/a file.md>
Run `scripts/check.py`, then the `example` skill.
''', 'name: "example"\ndescription: >-\n  A multiline\n  description.')
        self.assertEqual([], MODULE.lint(self.root))

    def test_missing_metadata_and_entrypoint(self):
        for metadata in ('description: text', 'name: example', 'name: example\ndescription: ""',
                         'name: example\ndescription: >-\n'):
            with self.subTest(metadata=metadata):
                self.write_skill(metadata=metadata)
                self.assertIn('frontmatter requires', self.findings())
        self.write_skill(metadata='name: wrong\ndescription: text')
        self.assertIn('frontmatter name must be example', self.findings())
        (self.skill / 'SKILL.md').unlink()
        self.assertIn('missing SKILL.md', self.findings())

    def test_missing_inline_reference_and_script_paths(self):
        self.write_skill('''[missing](missing.md#part)
[ref]: references/missing.md
Run `scripts/missing.py`.
''')
        findings = self.findings()
        for target in ('missing.md', 'references/missing.md', 'scripts/missing.py'):
            self.assertIn(f'missing relative resource: {target}', findings)

    def test_nonportable_paths_and_unknown_skills_in_reference(self):
        (self.skill / 'details.md').write_text(
            'Path /Users/someone/code\nUse `missing-one` skill or skill `missing-two`.')
        findings = self.findings()
        self.assertIn('details.md:1: nonportable', findings)
        self.assertIn('unknown skill: missing-one', findings)
        self.assertIn('unknown skill: missing-two', findings)

    def test_required_guard_executable(self):
        self.executable.chmod(0o644)
        self.assertIn("agent-guard executable is missing or not executable", self.findings())
        self.executable.unlink()
        self.assertIn("agent-guard executable is missing or not executable", self.findings())

    def test_dangling_and_non_skill_symlinks(self):
        directory = self.root / 'config/codex/skills'
        (directory / 'dangling').symlink_to('../../skills/absent')
        (directory / 'wrong').symlink_to('../../skills')
        findings = self.findings()
        self.assertIn('skills/dangling:1: dangling', findings)
        self.assertIn('skills/wrong:1: dangling', findings)

    def test_shared_skill_missing_from_harness(self):
        (self.root / 'config/copilot/skills/example').unlink()
        findings = self.findings()
        self.assertIn('config/copilot/skills:1: missing harness link for skill: example', findings)
        self.assertNotIn('config/claude/skills:1: missing harness link', findings)


    def add_review_pair(self):
        for name in MODULE.REVIEW_SKILLS:
            folder = self.root / 'config/skills' / name
            folder.mkdir()
            (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Review.\n---\n')
            for relative in MODULE.REVIEW_SHARED_FILES:
                resource = folder / relative
                resource.parent.mkdir(parents=True, exist_ok=True)
                resource.write_text('Shared resource.\n')
            for harness in MODULE.HARNESSES:
                (self.root / 'config' / harness / 'skills' / name).symlink_to(f'../../skills/{name}')

    def test_review_shared_resources_detect_drift_and_missing_pair(self):
        self.add_review_pair()
        self.assertEqual([], MODULE.lint(self.root))
        for relative in ('references/review-protocol.md', 'references/focused-reviews.md'):
            with self.subTest(relative=relative):
                path = self.root / 'config/skills/pr-review2' / relative
                original = path.read_bytes()
                path.write_text('Different routing policy.\n')
                self.assertIn('shared review resource differs', self.findings())
                path.unlink()
                self.assertIn('missing shared review resource', self.findings())
                path.write_bytes(original)

    def test_review_skill_cannot_be_installed_without_its_pair(self):
        folder = self.root / 'config/skills/code-review-expert2'
        folder.mkdir()
        (folder / 'SKILL.md').write_text('---\nname: code-review-expert2\ndescription: Review.\n---\n')
        self.assertIn('missing paired review skill', self.findings())

    def add_review_eval(self):
        self.add_review_pair()
        evaluation = self.root / 'config/skills/pr-review2/eval'
        self.eval_cases = evaluation / 'cases'
        for name, oracle in (
                ('01-sync-a', '# Oracle\n\n## Class recognition\n\nNamed.\n\n'
                              '## Instance recall\n\n- src/a.py:3 - one\n  wrapped\n'
                              '- src/b.py:4 - two\n'),
                ('02-sync-b', '# Oracle\n\n## False blockers\n\nTarget 0.\n')):
            case = self.eval_cases / name
            case.mkdir(parents=True)
            (case / 'input.md').write_text('Neutral synthetic review input.\n')
            (case / 'oracle.md').write_text(oracle)
        self.registry = evaluation / 'classes.md'
        self.write_registry(CLASS_ROW.format('02-sync-b'))
        self.results = evaluation / 'results'
        self.results.mkdir()
        (self.results / 'README.md').write_text('Format notes without a header.\n')

    def write_registry(self, *rows):
        self.registry.write_text('# Registry\n\n| Key | Invariant | Seeded instances | Seeded cases'
                                 ' | Control cases | Target |\n|---|---|---|---|---|---|\n'
                                 + ''.join(f'{row}\n' for row in rows))

    def write_result(self, **fields):
        header = {'reviewer': 'pr-review2', 'skill-version': '2.5.0',
                  'candidate-sha256': 'a' * 64, 'case': '01-sync-a',
                  'host': 'agent-cli 1.0', 'model': 'model-id'}
        header.update(fields)
        lines = ''.join(f'{key}: {value}\n' for key, value in header.items() if value is not None)
        (self.results / '2026-01-01-01-sync-a-agent.md').write_text(f'{lines}\nRaw output.\n')

    def test_review_eval_valid_structure(self):
        self.add_review_eval()
        self.write_result()
        self.assertEqual([], MODULE.lint(self.root))

    def test_review_eval_case_requires_input_and_oracle(self):
        self.add_review_eval()
        (self.eval_cases / '01-sync-a/oracle.md').unlink()
        (self.eval_cases / '02-sync-b/input.md').write_text('  \n')
        findings = self.findings()
        self.assertIn('01-sync-a/oracle.md:1: eval case requires nonempty oracle.md', findings)
        self.assertIn('02-sync-b/input.md:1: eval case requires nonempty input.md', findings)

    def test_review_eval_registry_rows(self):
        self.add_review_eval()
        cases = {
            '| `Bad Key` | Inv | 2 | 01-sync-a | none | reviewer eval |':
                'class key must be <surface>.<broken-invariant>: Bad Key',
            '| `path.same-file` | Inv | 2 | 01-sync-a | reviewer eval |':
                'class row needs 6 columns',
            '| `path.same-file` | Inv | 2 | 09-absent | none | reviewer eval |':
                'names unknown eval case: 09-absent',
            '| `path.same-file` | Inv | 0 | 01-sync-a | none | reviewer eval |':
                'requires a positive seeded instance count',
            '| `path.same-file` | Inv | 2 | none | 02-sync-b | reviewer eval |':
                'requires a seeded case',
            '| `path.same-file` |  | 2 | 01-sync-a | none |  |':
                'requires an invariant and a target',
        }
        for row, message in cases.items():
            with self.subTest(row=row):
                self.write_registry(row)
                self.assertIn(message, self.findings())
        self.write_registry(CLASS_ROW.format('none'), CLASS_ROW.format('none'))
        self.assertIn('duplicate class key: path.same-file', self.findings())
        self.write_registry()
        self.assertIn('defect class registry has no class rows', self.findings())
        self.registry.unlink()
        self.assertIn('missing defect class registry', self.findings())

    def test_review_eval_oracle_sections_and_instance_count(self):
        self.add_review_eval()
        seeded = self.eval_cases / '01-sync-a/oracle.md'
        seeded.write_text('# Oracle\n\n## Class recognition\n\nNamed.\n')
        (self.eval_cases / '02-sync-b/oracle.md').write_text('# Oracle\n\nNo sections.\n')
        findings = self.findings()
        self.assertIn('requires section: Instance recall', findings)
        self.assertIn('requires section: False blockers', findings)
        seeded.write_text('## Class recognition\n\n## Instance recall\n\n- src/a.py:3\n'
                          '## False blockers\n\n- src/b.py:4\n')
        self.assertIn('instance recall lists 1 path:line anchors; class path.same-file registers 2',
                      self.findings())
        seeded.write_text('## Class recognition\n\n## Instance recall\n\n- src/a.py:3\n'
                          '- src/b.py:4\n- src/c.py:5\n')
        self.assertIn('instance recall lists 3 path:line anchors; class path.same-file registers 2',
                      self.findings())

    def test_review_eval_inputs_and_names_must_not_reveal_class(self):
        self.add_review_eval()
        for text in ('Look for path.same-file here.', 'A same-file bug.', 'The Same File rule.'):
            with self.subTest(text=text):
                (self.eval_cases / '01-sync-a/input.md').write_text(text)
                self.assertIn('01-sync-a/input.md:1: eval input reveals class path.same-file',
                              self.findings())
        (self.eval_cases / '01-sync-a/input.md').write_text('Neutral.\n')
        (self.eval_cases / '01-sync-a').rename(self.eval_cases / '01-same-check')
        self.write_registry('| `path.same-file` | Inv | 2 | 01-same-check | none | reviewer eval |')
        self.assertIn('eval case name reveals class path.same-file: 01-same-check', self.findings())

    def test_review_eval_result_binds_reviewer_identity(self):
        self.add_review_eval()
        for field in MODULE.RESULT_FIELDS:
            with self.subTest(field=field):
                self.write_result(**{field: None})
                self.assertIn(f'result requires reviewer identity field: {field}', self.findings())
        cases = {
            'reviewer': ('no-mistakes', 'result reviewer must be pr-review2'),
            'skill-version': ('latest', 'result skill-version must be a metadata.version'),
            'candidate-sha256': ('abc', 'result candidate-sha256 must be 64 lowercase hex digits'),
            'case': ('09-absent', 'result names unknown eval case: 09-absent'),
        }
        for field, (value, message) in cases.items():
            with self.subTest(field=field, value=value):
                self.write_result(**{field: value})
                self.assertIn(message, self.findings())


if __name__ == '__main__':
    unittest.main()
